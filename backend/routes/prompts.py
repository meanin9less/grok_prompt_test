from fastapi import APIRouter
from services.prompts.prompts import PROMPTS

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.get("/list")
async def get_prompts_list():
    """
    사용 가능한 모든 프롬프트 목록을 반환합니다.
    """
    prompt_list = list(PROMPTS.keys())
    return {
        "prompts": prompt_list,
        "total": len(prompt_list)
    }


@router.get("/{prompt_key}")
async def get_prompt(prompt_key: str):
    """
    특정 프롬프트 내용을 반환합니다.

    Parameters:
    - prompt_key: 프롬프트의 키 (예: "prompt")
    """
    if prompt_key not in PROMPTS:
        return {
            "error": f"Prompt '{prompt_key}' not found",
            "available_prompts": list(PROMPTS.keys())
        }

    return {
        "key": prompt_key,
        "content": PROMPTS[prompt_key]
    }
