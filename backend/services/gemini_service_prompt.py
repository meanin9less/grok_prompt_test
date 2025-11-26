import httpx
import json
from config.settings import settings
from services.prompts.gemini_prompt import GEMINI_PROMPTS


class GeminiServicePrompt:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.base_url = settings.gemini_api_base_url
        self.model = settings.gemini_model

    async def chat(self, message: str, history: list = None, prompt_key: str = "prompt"):
        """
        Gemini API에 프롬프트를 포함하여 메시지를 보내고 스트림 형식으로 응답을 받습니다.
        """
        system_prompt = GEMINI_PROMPTS.get(prompt_key, GEMINI_PROMPTS.get("prompt", ""))

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "messages": messages,
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
                        f"Gemini API Error {response.status_code}: {await response.aread().decode()}"
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


gemini_service_prompt = GeminiServicePrompt()
