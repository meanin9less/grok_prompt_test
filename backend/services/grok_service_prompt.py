import httpx
import json
from config.settings import settings


class GrokServicePrompt:
    def __init__(self):
        self.api_key = settings.grok_api_key
        self.base_url = settings.grok_api_base_url
        self.model = settings.grok_model

    async def chat(self, prompt:str, message: str) -> str:
        """
        Grok API에 메시지를 보내고 응답을 받습니다.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Grok API Error {response.status_code}: {response.text}"
                )

            response_data = response.json()

            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]

            return ""
    

grok_service_prompt = GrokServicePrompt()
