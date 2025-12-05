import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services import grok_service_prompt, openai_service_prompt, gemini_service_prompt
from utils import GrokAPIError
from schemas import AiHubRequest, AiHubStreamHandshake, AiHubStreamChunk

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

router = APIRouter(prefix="/api/chat", tags=["chat-unified"])
ai_hub_router = APIRouter(prefix="/api/ai_hub", tags=["ai-hub"])


@ai_hub_router.post(
    "/get_prompt_res_text",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "SSE stream: first event is handshake {req_id, result_code, result_msg}, followed by ai_output chunks.",
            "content": {
                "text/event-stream": {
                    "example": """
data: {"req_id":"abc-123","result_code":0,"result_msg":"ok"}

data: {"ai_output":"안녕하세요"}

data: {"ai_output":" 반갑습니다"}

"""
                }
            },
        }
    },
)
async def get_prompt_res_text(request: AiHubRequest):
    if not request.req_id or not str(request.req_id).strip():
        raise HTTPException(status_code=400, detail="req_id cannot be empty")

    if not request.user_input:
        raise HTTPException(status_code=400, detail="user_input cannot be empty")

    ui_type = (request.user_input.type or "text").lower()
    message_text = ""
    input_title = request.user_input.title or request.req_id

    try:
        req_snapshot = request.model_dump()
    except Exception:
        req_snapshot = {
            "req_id": request.req_id,
            "model": request.model,
            "version": request.version,
            "user_input": getattr(request, "user_input", None),
        }

    logger.info(
        "[AIHub] Incoming",
        extra={
            "req_id": request.req_id,
            "ui_type": ui_type,
            "has_form": bool(request.user_input.form),
            "form_keys": list(request.user_input.form.keys()) if isinstance(request.user_input.form, dict) else [],
            "has_text": bool(request.user_input.text),
            "req": req_snapshot,
        },
    )

    if ui_type == "form" or (request.user_input.form and not request.user_input.text):
        fields_text_parts = []
        labels_by_name = {}
        template = getattr(request.user_input, "template", None)

        fields = request.user_input.form or {}

        if template and getattr(template, "fields", None):
            for f in template.fields:
                name = getattr(f, "name", None)
                label = getattr(f, "label", None)
                value = getattr(f, "value", None)
                if name is None:
                    continue
                labels_by_name[name] = label or name
                # 값이 비어 있으면 form dict에서 보충
                if value is None and isinstance(fields, dict) and name in fields:
                    value = fields.get(name)
                fields_text_parts.append(f"{(label or name).strip()}: {'' if value is None else value}")

        if not fields_text_parts:
            if not isinstance(fields, dict) or not fields:
                raise HTTPException(status_code=400, detail="form fields cannot be empty")

            def _labelize(key):
                name = str(key)
                return labels_by_name.get(name, name.replace("_", " ").strip().title())

            fields_text_parts = [f"{_labelize(k)}: {v}" for k, v in fields.items()]

        fields_text = "\n".join(fields_text_parts)
        message_text = f"[Form Submission]\n{fields_text}" if fields_text else "[Form Submission]"
        logger.info(
            "[AIHub] Form submission payload",
            extra={
                "req_id": request.req_id,
                "provider": request.model or request.version or "default",
                "field_keys": list(fields.keys()) if isinstance(fields, dict) else [],
                "labels_used": labels_by_name,
                "payload_preview": message_text[:200],
            },
        )
    else:
        message_text = request.user_input.text or ""
        if not str(message_text).strip():
            raise HTTPException(status_code=400, detail="user_input text cannot be empty")

    prompt_text = request.prompt.text or ""

    provider = (request.model or "").lower()
    version_lower = (request.version or "").lower()

    if provider:
        if 'gpt' in provider or 'openai' in provider or 'o1' in provider:
            service = openai_service_prompt
        elif 'gemini' in provider:
            service = gemini_service_prompt
        else:
            service = grok_service_prompt
    else:
        if 'gpt' in version_lower or 'o1' in version_lower or 'openai' in version_lower:
            service = openai_service_prompt
        elif 'gemini' in version_lower:
            service = gemini_service_prompt
        else:
            service = grok_service_prompt

    try:
        async def generate():
            def _hist_text(item):
                if isinstance(item, dict):
                    return item.get("text") or ""
                return getattr(item, "text", "") or ""

            history = [{"role": "user", "content": _hist_text(item)} for item in request.hist] if request.hist else []

            # LLM 호출 직전, 텍스트로 정제된 메시지 로그
            logger.info(
                "[AIHub] LLM request ready",
                extra={
                    "req_id": request.req_id,
                    "provider": request.model or request.version or "default",
                    "model_version": request.version or "",
                    "history_len": len(history),
                    "message_preview": message_text[:500],
                    "prompt_len": len(prompt_text or ""),
                },
            )
            # 검증 성공 알림을 첫 SSE 이벤트로 전송
            handshake = {
                "req_id": request.req_id,
                "result_code": 0,
                "result_msg": "ok",
            }
            yield f"data: {json.dumps(handshake)}\n\n"

            async for chunk in service.stream_prompt_response(
                message_text,
                history,
                model=request.model,
                prompt_text=prompt_text,
                model_version=request.version,
                req_id=input_title or request.req_id,
            ):
                yield chunk

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise GrokAPIError(detail=str(e))
