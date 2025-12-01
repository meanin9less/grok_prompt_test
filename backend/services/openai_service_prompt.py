import httpx
import json
import logging
from config.settings import settings
from services.prompts.prompts import PROMPTS

logger = logging.getLogger(__name__)


class OpenAIServicePrompt:
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.base_url = settings.openai_api_base_url
        self.model = settings.openai_model

    async def chat(self, message: str, history: list = None, prompt_key: str = "prompt", model: str = None, system_prompt: str = None, model_info: dict = None, input_title: str = None):
        """
        OpenAI API에 프롬프트를 포함하여 메시지를 보내고 스트림 형식으로 응답을 받습니다.

        Parameters:
        - message: 사용자 메시지
        - history: 대화 히스토리
        - prompt_key: 사용할 프롬프트 키
        - model: 사용할 모델 (미지정 시 기본값 사용)
        """
        system_prompt = system_prompt if system_prompt is not None else PROMPTS.get(prompt_key, PROMPTS.get("prompt", ""))
        logger.info("[Service] chat call", extra={"model": model or self.model, "model_info": model_info, "input_title": input_title, "prompt_key": prompt_key, "system_prompt_len": len(system_prompt or "")})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        # 요청에서 지정한 모델 또는 기본값 사용
        use_model = model if model else self.model
        logger.info(f"OpenAI Chat - Using model: {use_model} (requested: {model}, default: {self.model})")

        payload = {
            "model": use_model,
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
                        f"OpenAI API Error {response.status_code}: {await response.aread().decode()}"
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


openai_service_prompt = OpenAIServicePrompt()
