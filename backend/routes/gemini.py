from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from services import gemini_service_prompt
from utils import GrokAPIError

router = APIRouter(prefix="/api/gemini", tags=["gemini"])


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []


class ChatResponse(BaseModel):
    response: str


@router.post("/prompt-chat")
async def prompt_chat(request: ChatRequest):
    """
    Gemini API에 프롬프트를 포함하여 메시지를 보내고 스트림 형식으로 응답을 받습니다.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        async def generate():
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]
            async for chunk in gemini_service_prompt.chat(request.message, history):
                yield chunk

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise GrokAPIError(detail=str(e))


@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "gemini-api"}
