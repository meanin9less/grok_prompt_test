from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services import grok_service_prompt, openai_service_prompt, gemini_service_prompt
from utils import GrokAPIError
from .schemas import AiHubRequest

router = APIRouter(prefix="/api/chat", tags=["chat-unified"])
ai_hub_router = APIRouter(prefix="/api/ai_hub", tags=["ai-hub"])


@ai_hub_router.post("/get_prompt_res_text")
async def get_prompt_res_text(request: AiHubRequest):
    if not request.user_input:
        raise HTTPException(status_code=400, detail="user_input cannot be empty")

    message_text = request.user_input.text or ""
    input_title = request.user_input.title or request.req_id

    if not str(message_text).strip():
        raise HTTPException(status_code=400, detail="user_input text cannot be empty")

    prompt_text = request.prompt.text or ""

    # 입력값 로깅
    print(f"\n{'='*60}")
    print(f"[AI Hub Request]")
    print(f"req_id: {request.req_id}")
    print(f"model: {request.model}")
    print(f"version: {request.version}")
    print(f"prompt: {request.prompt}")
    print(f"user_input: {request.user_input}")
    print(f"hist count: {len(request.hist) if request.hist else 0}")
    print(f"{'='*60}\n")

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
            history = [{"role": "user", "content": item.text or ""} for item in request.hist] if request.hist else []
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
