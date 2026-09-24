from .health import router as health_router
from .predictions import router as predictions_router
from .model import router as model_router
from .hardware import router as hardware_router
from .categories import router as categories_router

__all__ = [
    "health_router",
    "predictions_router",
    "model_router",
    "hardware_router",
    "categories_router",
]
