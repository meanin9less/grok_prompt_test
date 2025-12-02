from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from services import grok_service_prompt, openai_service_prompt, gemini_service_prompt
from utils import GrokAPIError

router = APIRouter(prefix="/api/chat", tags=["chat-unified"])
ai_hub_router = APIRouter(prefix="/api/ai_hub", tags=["ai-hub"])


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []
    model: Optional[str] = None  # grok | gemini | openai
    model_version: Optional[str] = None  # 세부 버전
    prompt: Optional[str] = None
    input_title: Optional[str] = None


class AiHubRequest(BaseModel):
    req_id: Optional[str] = None
    model: Optional[str] = None
    version: Optional[str] = None
    prompt: Optional[str] = None
    hist: List[Message] = []
    user_input: str


@router.post("/prompt-chat")
async def prompt_chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # 입력값 로깅
    print(f"\n{'='*60}")
    print(f"[Chat Request]")
    print(f"Message: {request.message}")
    print(f"Model: {request.model}")
    print(f"Model Version: {request.model_version}")
    print(f"Prompt: {request.prompt[:100] if request.prompt else 'None'}{'...' if request.prompt and len(request.prompt) > 100 else ''}")
    print(f"Input Title: {request.input_title}")
    print(f"History Count: {len(request.history)}")
    print(f"{'='*60}\n")

    provider = (request.model or "").lower()
    version_lower = (request.model_version or "").lower()

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
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]
            async for chunk in service.chat(
                request.message,
                history,
                model=request.model,
                prompt=request.prompt,
                model_version=request.model_version,
                input_title=request.input_title,
            ):
                yield chunk

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise GrokAPIError(detail=str(e))


@ai_hub_router.post("/get_prompt_res_text")
async def get_prompt_res_text(request: AiHubRequest):
    if not request.user_input or not request.user_input.strip():
        raise HTTPException(status_code=400, detail="user_input cannot be empty")

    # 입력값 로깅
    print(f"\n{'='*60}")
    print(f"[AI Hub Request]")
    print(f"req_id: {request.req_id}")
    print(f"model: {request.model}")
    print(f"version: {request.version}")
    print(f"prompt: {request.prompt[:100] if request.prompt else 'None'}{'...' if request.prompt and len(request.prompt) > 100 else ''}")
    print(f"user_input: {request.user_input[:120]}{'...' if len(request.user_input) > 120 else ''}")
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
            history = [{"role": msg.role, "content": msg.content} for msg in request.hist]
            async for chunk in service.chat(
                request.user_input,
                history,
                model=request.model,
                prompt=request.prompt,
                model_version=request.version,
                input_title=request.req_id,
            ):
                yield chunk

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise GrokAPIError(detail=str(e))
