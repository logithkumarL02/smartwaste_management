"""
SmartWaste FastAPI Backend - Entry point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .inference.model_loader import load_model
from .hardware.controller import get_sorting_device

log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    log.info("SmartWaste API starting up...")
    model_available = load_model(settings.model_path, settings.model_metadata_path)
    if model_available:
        log.info("✓ Model loaded successfully.")
    else:
        log.warning(
            "⚠ Model not available. Classify endpoints return 503. "
            "Train with: python ml/train.py"
        )
    device = get_sorting_device(settings.hardware_mode)
    log.info(f"✓ Hardware mode: {device.get_mode()}")
    yield
    log.info("SmartWaste API shutting down.")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="SmartWaste API",
        description="AI-powered waste segregation REST API.",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    from .api.routes.health import router as health_router
    from .api.routes.predictions import router as pred_router
    from .api.routes.model import router as model_router
    from .api.routes.hardware import router as hw_router
    from .api.routes.categories import router as cat_router

    app.include_router(health_router)
    app.include_router(pred_router)
    app.include_router(model_router)
    app.include_router(hw_router)
    app.include_router(cat_router)

    return app


app = create_app()
