"""Main waste classifier - preprocessing + inference + uncertainty handling."""

import logging
from typing import Optional

import numpy as np

from .preprocessing import validate_and_preprocess, PreprocessingError
from .model_loader import predict_raw, is_model_available, get_metadata
from ..disposal.categories import (
    get_recommendation,
    get_display_name,
    get_hardware_command,
)

log = logging.getLogger(__name__)


class ClassificationResult:
    def __init__(
        self,
        category,
        display_name,
        confidence,
        is_uncertain,
        recommendation,
        hardware_command,
        model_version,
        message=None,
        alternatives=None,
    ):
        self.category = category
        self.display_name = display_name
        self.confidence = confidence
        self.is_uncertain = is_uncertain
        self.recommendation = recommendation
        self.hardware_command = hardware_command
        self.model_version = model_version
        self.message = message
        self.alternatives = alternatives

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "display_name": self.display_name,
            "confidence": self.confidence,
            "is_uncertain": self.is_uncertain,
            "recommendation": self.recommendation,
            "hardware_command": self.hardware_command,
            "model_version": self.model_version,
            "message": self.message,
            "alternatives": self.alternatives,
        }


def classify(
    image_bytes: bytes,
    mime_type: Optional[str] = None,
    confidence_threshold: float = 0.80,
    uncertain_threshold: float = 0.50,
    max_alternatives: int = 3,
) -> ClassificationResult:

    print("\n🔥🔥🔥 CLASSIFY FUNCTION IS RUNNING 🔥🔥🔥")

    if not is_model_available():
        raise RuntimeError(
            "No trained model available. Run: python ml/train.py"
        )

    metadata = get_metadata()

    class_names = metadata["class_names"]
    image_size = metadata["image_size"]
    model_version = metadata["model_version"]

    print("Classes:", class_names)
    print("Image size:", image_size)
    print("Model version:", model_version)

    # ==========================================
    # PREPROCESS IMAGE
    # ==========================================

    img_array = validate_and_preprocess(
        image_bytes,
        target_size=image_size,
        mime_type=mime_type,
    )

    print("\n===== IMAGE INPUT DEBUG =====")
    print("Image shape :", img_array.shape)
    print("Image dtype :", img_array.dtype)
    print("Image min   :", img_array.min())
    print("Image max   :", img_array.max())
    print("Image mean  :", img_array.mean())
    print("=============================")

    # ==========================================
    # MODEL PREDICTION
    # ==========================================

    probs, _ = predict_raw(img_array)

    print("\n🔥🔥🔥 MODEL PROBABILITIES 🔥🔥🔥")

    for i, probability in enumerate(probs):
        print(
            f"{i} - {class_names[i]:20s}: "
            f"{float(probability):.6f} "
            f"({float(probability) * 100:.2f}%)"
        )

    print("Probability sum:", float(probs.sum()))

    # ==========================================
    # TOP PREDICTION
    # ==========================================

    top_idx = int(np.argmax(probs))
    top_conf = float(probs[top_idx])
    top_category = class_names[top_idx]

    print("\n🔥🔥🔥 TOP PREDICTION 🔥🔥🔥")
    print("Top index      :", top_idx)
    print("Top category   :", top_category)
    print(
        "Top confidence :",
        f"{top_conf:.6f} ({top_conf * 100:.2f}%)",
    )
    print("====================================\n")

    # ==========================================
    # UNCERTAIN PREDICTION
    # ==========================================

    if top_conf < uncertain_threshold:
        return ClassificationResult(
            category="unknown",
            display_name="Unknown",
            confidence=round(top_conf, 4),
            is_uncertain=True,
            recommendation="Unable to classify. Please sort manually.",
            hardware_command="MANUAL_REVIEW",
            model_version=model_version,
            message=(
                "The system is not sufficiently confident. "
                "Please verify manually before disposal."
            ),
        )

    # ==========================================
    # ALTERNATIVE PREDICTIONS
    # ==========================================

    sorted_indices = np.argsort(probs)[::-1][:max_alternatives]

    alternatives = [
        {
            "category": class_names[i],
            "confidence": round(float(probs[i]), 4),
        }
        for i in sorted_indices
    ]

    # Prediction below 80% but above 50%
    is_uncertain = top_conf < confidence_threshold

    return ClassificationResult(
        category=top_category,
        display_name=get_display_name(top_category),
        confidence=round(top_conf, 4),
        is_uncertain=is_uncertain,
        recommendation=get_recommendation(top_category),
        hardware_command=get_hardware_command(top_category),
        model_version=model_version,
        message=(
            "Prediction has low confidence. Please verify before disposal."
            if is_uncertain
            else None
        ),
        alternatives=alternatives if is_uncertain else None,
    )