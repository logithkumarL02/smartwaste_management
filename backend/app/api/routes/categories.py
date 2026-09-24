from fastapi import APIRouter
from ...disposal.categories import list_categories

router = APIRouter(prefix="/api", tags=["categories"])

@router.get("/categories")
async def get_categories():
    return {"categories": list_categories()}
