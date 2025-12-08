import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from db.session import get_session
from db.models import Template

router = APIRouter(prefix="/api/templates", tags=["templates"])


class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    schema: dict = Field(..., description="최초 버전 템플릿 스냅샷")


@router.get("")
async def list_templates(session=Depends(get_session)):
    result = await session.execute(
        select(Template).order_by(Template.updated_at.desc())
    )
    rows = result.scalars().all()
    return rows


@router.get("/{template_id}")
async def get_template(template_id: uuid.UUID, session=Depends(get_session)):
    tmpl = await session.get(Template, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return tmpl


@router.post("")
async def create_template(payload: TemplateCreate, session=Depends(get_session)):
    tmpl = Template(
        name=payload.name,
        description=payload.description,
        labels=payload.labels,
        schema=payload.schema,
    )
    session.add(tmpl)
    await session.flush()
    return {"id": tmpl.id}
