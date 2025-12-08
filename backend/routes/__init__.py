from .ai_hub import router
from .text_submit import ai_hub_router
from .templates_api import router as templates_router

__all__ = ["router", "ai_hub_router", "templates_router"]
