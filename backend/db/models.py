import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, JSON, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ModelInfo(Base):
    """
    모델/세부모델 메타 테이블: 모델 이름과 버전만 관리.
    """
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)   # 모델 PK
    model = Column(Text, nullable=False)                                    # 공급자/계열(openai/gemini/grok 등)
    version = Column(Text, nullable=False)                                  # 모델 버전/세부모델(gpt-4.1 등)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)                 # 생성 시각
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)                 # 업데이트 시각


class Prompt(Base):
    """
    프롬프트 템플릿 저장 테이블.
    """
    __tablename__ = "prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)   # 프롬프트 PK
    title = Column(Text, nullable=False)                                    # 프롬프트 제목
    content = Column(Text, nullable=False)                                  # 프롬프트 내용
    description = Column(Text)                                              # 설명
    labels = Column(JSON, default=list)                                     # 태그/라벨
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)


class Template(Base):
    """
    폼/버튼/액션 등을 담는 템플릿 정의(JSON Schema/UiSchema)를 저장.
    """
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)   # 템플릿 PK
    name = Column(Text, nullable=False)                                     # 템플릿 이름
    description = Column(Text)                                              # 템플릿 설명
    labels = Column(JSON, default=list)                                     # 태그/라벨
    schema = Column(JSON, nullable=False)                                   # 템플릿 전체 JSON(Schema/UiSchema)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)


class UserInput(Base):
    """
    실행 시 사용될 입력 정의 저장: 모델/버전/프롬프트/입력 타입 및 값.
    """
    __tablename__ = "user_input"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)   # 입력 정의 PK
    template_id = Column(UUID(as_uuid=True))                                # 연결된 템플릿 ID(폼일 때)
    model = Column(Text, nullable=False)                                    # 모델
    version = Column(Text)                                                  # 세부모델/버전
    prompt = Column(Text)                                                   # 프롬프트(문자열)
    input_type = Column(Text, nullable=False)                               # text | form
    input_text = Column(Text)                                               # 텍스트 입력값
    input_form = Column(JSON)                                               # 폼 입력값 {field:value}
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
