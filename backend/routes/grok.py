from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services import grok_service_basic
from utils import GrokAPIError

router = APIRouter(prefix="/api/grok", tags=["grok"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Grok API에 메시지를 보내고 스트림 형식으로 응답을 받습니다.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        async def generate():
            async for chunk in grok_service_basic.chat(request.message):
                yield chunk

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise GrokAPIError(detail=str(e))




@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "grok-api"}
