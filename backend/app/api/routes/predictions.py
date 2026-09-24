"""Prediction routes - upload and webcam classification."""
import base64
import logging
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Header
from ...config import get_settings, Settings
from ...inference.classifier import classify
from ...inference.preprocessing import PreprocessingError
from ...schemas.prediction import PredictionResponse
from ...services.prediction_service import save_prediction

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["predictions"])

def _check_size(content_length: Optional[int], settings: Settings):
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if content_length and content_length > max_bytes:
        raise HTTPException(status_code=413, detail=f"File too large. Max: {settings.max_upload_size_mb} MB.")

@router.post("/predict", response_model=PredictionResponse)
async def predict_upload(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
    content_length: Optional[int] = Header(None),
    settings: Settings = Depends(get_settings),
):
    _check_size(content_length, settings)
    if file.content_type not in settings.allowed_mime_types:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {file.content_type}")
    image_bytes = await file.read()
    if len(image_bytes) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds size limit.")
    try:
        result = classify(image_bytes, mime_type=file.content_type,
                          confidence_threshold=settings.confidence_threshold,
                          uncertain_threshold=settings.uncertain_threshold,
                          max_alternatives=settings.max_alternatives)
    except PreprocessingError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        log.exception("Unexpected classification error")
        raise HTTPException(status_code=500, detail="Classification failed unexpectedly.")
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        await save_prediction(result, source="upload", token=token, settings=settings)
    return PredictionResponse(**result.to_dict())

@router.post("/predict/webcam", response_model=PredictionResponse)
async def predict_webcam(
    payload: dict,
    authorization: Optional[str] = Header(None),
    settings: Settings = Depends(get_settings),
):
    image_data_uri = payload.get("image", "")
    if not image_data_uri:
        raise HTTPException(status_code=422, detail="Missing 'image' field.")
    if "," in image_data_uri:
        header, b64_data = image_data_uri.split(",", 1)
        mime_type = header.split(":")[1].split(";")[0] if ":" in header else "image/jpeg"
    else:
        b64_data = image_data_uri
        mime_type = "image/jpeg"
    try:
        image_bytes = base64.b64decode(b64_data)
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid base64 image data.")
    if len(image_bytes) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Frame exceeds size limit.")
    try:
        result = classify(image_bytes, mime_type=mime_type,
                          confidence_threshold=settings.confidence_threshold,
                          uncertain_threshold=settings.uncertain_threshold,
                          max_alternatives=settings.max_alternatives)
    except PreprocessingError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        log.exception("Webcam classification error")
        raise HTTPException(status_code=500, detail="Classification failed unexpectedly.")
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        await save_prediction(result, source="webcam", token=token, settings=settings)
    return PredictionResponse(**result.to_dict())
