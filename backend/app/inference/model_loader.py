"""Singleton model loader - loads trained Keras model once at startup."""
import json
import logging
from pathlib import Path
from typing import Optional, Tuple
import numpy as np

log = logging.getLogger(__name__)

_model = None
_metadata: Optional[dict] = None
_model_loaded: bool = False

def load_model(model_path: str, metadata_path: str) -> bool:
    global _model, _metadata, _model_loaded
    if _model_loaded:
        return _model is not None
    model_file = Path(model_path)
    meta_file = Path(metadata_path)
    if not model_file.exists():
        log.warning(f"Model not found at {model_path}. Run: python ml/train.py")
        _model_loaded = True
        return False
    if not meta_file.exists():
        log.warning(f"Metadata not found at {metadata_path}.")
        _model_loaded = True
        return False
    try:
        import tensorflow as tf
        from tensorflow import keras
        log.info(f"Loading model from {model_path}...")
        _model = keras.models.load_model(str(model_file))
        with open(meta_file) as f:
            _metadata = json.load(f)
        log.info(f"Model loaded: {_metadata.get('model_version', 'unknown')}")
        _model_loaded = True
        return True
    except Exception as e:
        log.error(f"Failed to load model: {e}")
        _model_loaded = True
        return False

def get_model():
    return _model

def get_metadata() -> Optional[dict]:
    return _metadata

def is_model_available() -> bool:
    return _model is not None and _metadata is not None

def predict_raw(image_array: np.ndarray) -> Tuple[np.ndarray, dict]:
    if not is_model_available():
        raise RuntimeError("Model is not available. Train with: python ml/train.py")
    batch = np.expand_dims(image_array, axis=0)
    probs = _model.predict(batch, verbose=0)[0]
    return probs, _metadata
