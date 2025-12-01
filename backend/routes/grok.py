from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from services import grok_service_prompt
from utils import GrokAPIError

router = APIRouter(prefix="/api/grok", tags=["grok"])


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []
    model: Optional[str] = None
    prompt_key: Optional[str] = "prompt"
    system_prompt: Optional[str] = None
    model_info: Optional[Dict[str, Any]] = None
    input_title: Optional[str] = None


class ChatResponse(BaseModel):
    response: str


@router.post("/prompt-chat")
async def prompt_chat(request: ChatRequest):
    """
    Grok API에 프롬프트를 포함하여 메시지를 보내고 스트림 형식으로 응답을 받습니다.

    Parameters:
    - message: 사용자 메시지
    - history: 대화 히스토리 (선택사항)
    - model: 사용할 모델 (선택사항, 미지정 시 기본값 사용)
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        async def generate():
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]
            async for chunk in grok_service_prompt.chat(
                request.message,
                history,
                prompt_key=request.prompt_key,
                model=request.model,
                system_prompt=request.system_prompt,
                model_info=request.model_info,
                input_title=request.input_title
            ):
                yield chunk

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise GrokAPIError(detail=str(e))




@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "grok-api"}
