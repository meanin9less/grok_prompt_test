from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from services.prompts.prompts import PROMPTS

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


class PromptUpdate(BaseModel):
    content: str
    description: str | None = None  # 확장 대비, 현재는 content만 사용


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


@router.post("/{prompt_key}")
async def create_prompt(prompt_key: str, prompt_data: PromptUpdate):
  """
  새로운 프롬프트를 추가합니다.

  Parameters:
  - prompt_key: 프롬프트의 키
  - prompt_data: 생성할 프롬프트 내용
  """
  if prompt_key in PROMPTS:
      raise HTTPException(status_code=400, detail=f"Prompt '{prompt_key}' already exists")

  PROMPTS[prompt_key] = prompt_data.content
  return {
      "key": prompt_key,
      "content": PROMPTS[prompt_key],
      "message": "Prompt created successfully"
  }


@router.put("/{prompt_key}")
async def update_prompt(prompt_key: str, prompt_data: PromptUpdate):
    """
    특정 프롬프트 내용을 수정합니다.

    Parameters:
    - prompt_key: 프롬프트의 키
    - prompt_data: 수정할 프롬프트 내용
    """
    if prompt_key not in PROMPTS:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Prompt '{prompt_key}' not found",
                "available_prompts": list(PROMPTS.keys())
            }
        )

    PROMPTS[prompt_key] = prompt_data.content
    return {
        "key": prompt_key,
        "content": PROMPTS[prompt_key],
        "message": "Prompt updated successfully"
    }


@router.delete("/{prompt_key}")
async def delete_prompt(prompt_key: str):
    """
    특정 프롬프트를 삭제합니다.

    Parameters:
    - prompt_key: 프롬프트의 키
    """
    if prompt_key not in PROMPTS:
        return {
            "error": f"Prompt '{prompt_key}' not found",
            "available_prompts": list(PROMPTS.keys())
        }, 404

    del PROMPTS[prompt_key]
    return {
        "message": f"Prompt '{prompt_key}' deleted successfully",
        "remaining_prompts": list(PROMPTS.keys())
    }
