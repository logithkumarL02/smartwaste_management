from fastapi import APIRouter, Depends
from ...inference.model_loader import is_model_available, get_metadata
from ...schemas.prediction import ModelInfo
from ...config import get_settings

router = APIRouter(prefix="/api/model", tags=["model"])

@router.get("/info", response_model=ModelInfo)
async def get_model_info(settings=Depends(get_settings)):
    meta = get_metadata()
    if not is_model_available() or meta is None:
        return ModelInfo(
            model_version="not-trained", architecture="N/A", classes=0, class_names=[],
            image_size=224, confidence_threshold=settings.confidence_threshold,
            uncertain_threshold=settings.uncertain_threshold, model_available=False,
        )
    return ModelInfo(
        model_version=meta.get("model_version", "unknown"),
        architecture=meta.get("architecture", "unknown"),
        classes=meta.get("classes", 0), class_names=meta.get("class_names", []),
        image_size=meta.get("image_size", 224), trained_at=meta.get("trained_at"),
        confidence_threshold=settings.confidence_threshold,
        uncertain_threshold=settings.uncertain_threshold,
        missing_categories=meta.get("missing_categories", []), model_available=True,
    )
