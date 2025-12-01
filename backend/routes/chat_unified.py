from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from services import grok_service_prompt, openai_service_prompt, gemini_service_prompt
from utils import GrokAPIError

router = APIRouter(prefix="/api/chat", tags=["chat-unified"])


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


@router.post("/prompt-chat")
async def prompt_chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

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
