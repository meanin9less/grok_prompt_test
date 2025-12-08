from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Grok API Configuration
    grok_api_key: str
    grok_api_base_url: str = "https://api.x.ai/v1"
    grok_model: str = "grok-4-1-fast-reasoning"

    # OpenAI API Configuration
    openai_api_key: Optional[str] = None
    openai_api_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-5.1" # gpt-4o / gpt-4.1 / gpt-5.1

    # Gemini API Configuration
    gemini_api_key: Optional[str] = None
    gemini_api_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    gemini_model: str = "gemini-2.0-flash"

    # Database
    database_url: Optional[str] = None  # e.g., postgresql://grok:grokpass@localhost:5432/grokdb

    # FastAPI Configuration
    debug: bool = False
    app_name: str = "Grok API Backend"
    app_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
