import httpx
import json
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class GrokServicePrompt:
    def __init__(self):
        self.api_key = settings.grok_api_key
        self.base_url = settings.grok_api_base_url
        self.model = settings.grok_model

    async def stream_prompt_response(self, user_input_text: str, history: list = None, model: str = None, prompt_text: str = "", model_version: str | None = None, req_id: str | None = None):
        """
        Grok Native API(x.ai)로 프롬프트/입력을 보내고 스트림 응답을 반환합니다.
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
        logger.info(
            "[Grok] Native stream start",
            extra={
                "model": use_model,
                "default_model": self.model,
                "req_id": req_id,
                "history_len": len(history) if history else 0,
            },
        )

        payload = {
            "model": use_model,
            "messages": messages,
            "stream": True,
        }

        endpoint = f"{self.base_url}/chat/completions"

        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream(
                "POST",
                endpoint,
                json=payload,
                headers=headers,
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    raise Exception(f"Grok API Error {response.status_code}: {body.decode(errors='ignore')}")

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data:"):
                        data_str = line.split("data:", 1)[1].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue

                        choices = data.get("choices") or []
                        if not choices:
                            continue

                        delta = choices[0].get("delta", {}) or {}
                        content = delta.get("content") or ""
                        if isinstance(content, list):
                            content = "".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in content])

                        if content:
                            yield f"data: {json.dumps({'ai_output': content})}\n\n"


grok_service_prompt = GrokServicePrompt()
