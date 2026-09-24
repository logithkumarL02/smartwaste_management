from fastapi import APIRouter, HTTPException, Depends
from ...hardware.controller import get_sorting_device
from ...schemas.hardware import HardwareSortRequest, HardwareSortResponse, VALID_COMMANDS
from ...config import get_settings

router = APIRouter(prefix="/api/hardware", tags=["hardware"])

@router.post("/sort", response_model=HardwareSortResponse)
async def sort_waste(request: HardwareSortRequest, settings=Depends(get_settings)):
    if request.command not in VALID_COMMANDS:
        raise HTTPException(status_code=422, detail=f"Invalid command: {request.command}")
    device = get_sorting_device(settings.hardware_mode)
    success, message = device.sort(request.command)
    return HardwareSortResponse(success=success, command=request.command, mode=device.get_mode(), message=message)
