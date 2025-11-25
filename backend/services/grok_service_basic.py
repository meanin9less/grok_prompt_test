import httpx
import json
from config.settings import settings


class GrokServiceBasic:
    def __init__(self):
        self.api_key = settings.grok_api_key
        self.base_url = settings.grok_api_base_url
        self.model = settings.grok_model

    async def chat(self, message: str):
        """
        Grok API에 메시지를 보내고 스트림 형식으로 응답을 받습니다.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": message}],
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                if response.status_code != 200:
                    raise Exception(
                        f"Grok API Error {response.status_code}: {await response.aread().decode()}"
                    )

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue


grok_service_basic = GrokServiceBasic()
