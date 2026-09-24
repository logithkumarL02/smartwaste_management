from fastapi import APIRouter
from ...inference.model_loader import is_model_available, get_metadata
from ...hardware.controller import get_sorting_device
from ...config import get_settings

router = APIRouter()

@router.get("/health")
async def health_check():
    settings = get_settings()
    meta = get_metadata()
    device = get_sorting_device(settings.hardware_mode)
    return {
        "status": "ok",
        "model_available": is_model_available(),
        "model_version": meta.get("model_version") if meta else None,
        "hardware_mode": device.get_mode(),
        "hardware_available": device.is_available(),
    }
