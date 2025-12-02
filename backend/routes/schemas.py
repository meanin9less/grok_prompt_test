from typing import List, Optional
from pydantic import BaseModel

class UserInputText(BaseModel):
  id: Optional[str] = None
  title: Optional[str] = None
  text: Optional[str] = None


class Prompt(BaseModel):
  id: Optional[str] = None
  title: Optional[str] = None
  text: Optional[str] = None


class AiHubRequest(BaseModel):
  req_id: Optional[str] = None
  model: Optional[str] = None
  version: Optional[str] = None
  prompt: Prompt
  hist: List[UserInputText] = []
  user_input: UserInputText


class AiHubResponse(BaseModel):
  content: str
