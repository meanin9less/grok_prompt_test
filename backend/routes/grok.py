from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/check")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "api"}
