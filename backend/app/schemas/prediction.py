from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Alternative(BaseModel):
    category: str
    confidence: float

class PredictionResponse(BaseModel):
    category: str
    display_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_uncertain: bool
    recommendation: str
    hardware_command: str
    model_version: str
    message: Optional[str] = None
    alternatives: Optional[List[Alternative]] = None

class ModelInfo(BaseModel):
    model_version: str
    architecture: str
    classes: int
    class_names: List[str]
    image_size: int
    trained_at: Optional[str] = None
    confidence_threshold: float
    uncertain_threshold: float
    missing_categories: List[str] = []
    model_available: bool = True
