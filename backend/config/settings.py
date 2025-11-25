from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Grok API Configuration
    grok_api_key: str
    grok_api_base_url: str = "https://api.x.ai/v1"
    grok_model: str = "grok-4-1-fast-reasoning"

    # FastAPI Configuration
    debug: bool = False
    app_name: str = "Grok API Backend"
    app_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
