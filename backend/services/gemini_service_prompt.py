import httpx
import json
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class GeminiServicePrompt:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.base_url = settings.gemini_api_base_url
        self.model = settings.gemini_model

    async def stream_prompt_response(self, user_input_text: str, history: list = None, model: str = None, prompt_text: str = "", model_version: str | None = None, req_id: str | None = None):
        """
        Gemini Native API에 프롬프트/입력을 보내고 스트림 응답을 반환합니다.
        """
        prompt_text = prompt_text or ""
        use_model = model_version if model_version else self.model

        def _to_gemini_message(role: str, content: str):
            text = content if content is not None else ""
            if not str(text).strip():
                return None
            return {"role": role, "parts": [{"text": text}]}

        contents = []
        if history:
            for item in history:
                role = item.get("role") if isinstance(item, dict) else getattr(item, "role", "user")
                text = item.get("content") if isinstance(item, dict) else getattr(item, "content", "")
                msg = _to_gemini_message(role or "user", text or "")
                if msg:
                    contents.append(msg)

        user_msg = _to_gemini_message("user", user_input_text)
        if user_msg:
            contents.append(user_msg)

        payload: dict = {"contents": contents}
        if prompt_text:
            payload["system_instruction"] = {"parts": [{"text": prompt_text}]}

        logger.info(
            "[Gemini] Native stream start",
            extra={
                "model": use_model,
                "has_history": bool(history),
                "req_id": req_id,
            },
        )

        endpoint = f"{self.base_url}/models/{use_model}:streamGenerateContent"
        params = {"key": self.api_key, "alt": "sse"}
        headers = {"Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream(
                "POST",
                endpoint,
                params=params,
                json=payload,
                headers=headers,
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    raise Exception(f"Gemini API Error {response.status_code}: {body.decode(errors='ignore')}")

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data:"):
                        data_str = line.split("data:", 1)[1].strip()
                        if data_str in ("[DONE]", ""):
                            continue
                        try:
                            data = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue

                        candidates = data.get("candidates") or []
                        if not candidates:
                            continue

                        # Stream delta 또는 전체 content 모두 처리
                        content_obj = candidates[0].get("content") or {}
                        delta_obj = candidates[0].get("delta", {}).get("content", {})
                        parts = (content_obj.get("parts") or []) + (delta_obj.get("parts") or [])

                        for part in parts:
                            text = part.get("text") if isinstance(part, dict) else None
                            if text:
                                yield f"data: {json.dumps({'ai_output': text})}\n\n"
                    # Ignore other event types
                # Stream close -> nothing to do


gemini_service_prompt = GeminiServicePrompt()
