from pydantic import BaseModel
from typing import Optional

VALID_COMMANDS = {
    "SORT_PLASTIC", "SORT_METAL", "SORT_GLASS", "SORT_PAPER",
    "SORT_ORGANIC", "SORT_EWASTE", "SORT_TEXTILE", "SORT_OTHER",
    "MANUAL_REVIEW",
}

class HardwareSortRequest(BaseModel):
    command: str
    category: Optional[str] = None
    confidence: Optional[float] = None

class HardwareSortResponse(BaseModel):
    success: bool
    command: str
    mode: str
    message: str
