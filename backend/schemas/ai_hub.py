from typing import List, Optional
from pydantic import BaseModel

class UserInput(BaseModel):
  id: Optional[str] = None
  title: Optional[str] = None
  type: Optional[str] = "text"  # text | form
  text: Optional[str] = None
  form: Optional[dict] = None


class Prompt(BaseModel):
  id: Optional[str] = None
  title: Optional[str] = None
  text: Optional[str] = None


class AiHubRequest(BaseModel):
  req_id: Optional[str] = None
  model: Optional[str] = None
  version: Optional[str] = None
  prompt: Prompt
  hist: List = []
  user_input: UserInput


class AiHubResponse(BaseModel):
  content: str


class AiHubStreamHandshake(BaseModel):
  req_id: str
  result_code: int
  result_msg: str


class AiHubStreamChunk(BaseModel):
  ai_output: str


class FormUserInput(BaseModel):
  id: Optional[str] = None
  title: Optional[str] = None
  fields: dict
  user_agent: Optional[str] = None


class FormRequest(BaseModel):
  req_id: Optional[str] = None
  model: Optional[str] = None
  version: Optional[str] = None
  prompt: Prompt
  hist: List = []
  user_input: FormUserInput
