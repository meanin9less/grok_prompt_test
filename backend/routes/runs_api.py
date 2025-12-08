import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from db.session import get_session
from db.models import Run

router = APIRouter(prefix="/api/runs", tags=["runs"])


class RunCreate(BaseModel):
    template_id: Optional[uuid.UUID] = None
    template_version: Optional[int] = None
    model: str
    model_variant: Optional[str] = None
    system_prompt: Optional[str] = None
    input_type: str = Field(..., pattern="^(text|form)$")
    input_text: Optional[str] = None
    input_form: Optional[dict] = None
    template_snapshot: Optional[dict] = None
    output_payload: Optional[dict] = None


@router.post("")
async def create_run(payload: RunCreate, session=Depends(get_session)):
    run = Run(
        template_id=payload.template_id,
        template_version=payload.template_version,
        model=payload.model,
        model_variant=payload.model_variant,
        system_prompt=payload.system_prompt,
        input_type=payload.input_type,
        input_text=payload.input_text,
        input_form=payload.input_form,
        template_snapshot=payload.template_snapshot,
        output_payload=payload.output_payload,
    )
    session.add(run)
    await session.flush()
    return {"id": run.id, "created_at": run.created_at}


@router.get("")
async def list_runs(session=Depends(get_session)):
    result = await session.execute(
        select(Run.id, Run.template_id, Run.template_version, Run.model, Run.model_variant, Run.input_type, Run.created_at)
        .order_by(Run.created_at.desc())
        .limit(100)
    )
    return result.mappings().all()


@router.get("/{run_id}")
async def get_run(run_id: uuid.UUID, session=Depends(get_session)):
    run = await session.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
