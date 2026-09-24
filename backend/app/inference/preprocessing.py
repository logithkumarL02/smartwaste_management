"""OpenCV image preprocessing pipeline."""
import io
import logging
from typing import Optional
import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError

log = logging.getLogger(__name__)
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
MAX_DIMENSION = 4096

class PreprocessingError(Exception):
    pass

def validate_and_preprocess(image_bytes: bytes, target_size: int = 224, mime_type: str = None) -> np.ndarray:
    if not image_bytes:
        raise PreprocessingError("Empty image data received.")
    if mime_type and mime_type not in ALLOWED_MIME_TYPES:
        raise PreprocessingError(f"Unsupported image type: {mime_type}.")
    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        pil_img.verify()
    except UnidentifiedImageError:
        raise PreprocessingError("File is not a recognised image format.")
    except Exception as e:
        raise PreprocessingError(f"Corrupt or unreadable image: {e}")
    try:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise PreprocessingError(f"Cannot convert image to RGB: {e}")
    w, h = pil_img.size
    if w > MAX_DIMENSION or h > MAX_DIMENSION:
        raise PreprocessingError(f"Image dimensions ({w}x{h}) exceed maximum {MAX_DIMENSION}px.")
    img_array = np.array(pil_img, dtype=np.uint8)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    img_resized = cv2.resize(img_bgr, (target_size, target_size), interpolation=cv2.INTER_AREA)
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    return img_rgb.astype(np.float32)
