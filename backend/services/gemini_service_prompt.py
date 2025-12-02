import httpx
import json
import logging
from config.settings import settings
from services.prompts.prompts import PROMPTS

logger = logging.getLogger(__name__)


class GeminiServicePrompt:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.base_url = settings.gemini_api_base_url
        self.model = settings.gemini_model

    async def stream_prompt_response(self, user_input_text: str, history: list = None, model: str = None, prompt_text: str = "", model_version: str | None = None, req_id: str | None = None):
        """
        Gemini API에 프롬프트/입력을 보내고 스트림 응답을 반환합니다.
        """
        prompt_text = prompt_text or ""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = [{"role": "system", "content": prompt_text}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_input_text})

        # 요청에서 지정한 모델 또는 기본값 사용
        use_model = model_version if model_version else self.model
        logger.info(f"Gemini Chat - Using model: {use_model} (default: {self.model})")

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
                                    # JSON으로 감싸 개행이 이스케이프된 상태로 단일 SSE 라인에 실어 보낸다
                                    payload = json.dumps({"content": content})
                                    logger.debug(f"[Gemini Chunk] {repr(content[:50])}")
                                    yield f"data: {payload}\n\n"
                        except json.JSONDecodeError:
                            continue


gemini_service_prompt = GeminiServicePrompt()
