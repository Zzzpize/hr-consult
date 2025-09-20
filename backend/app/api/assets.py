from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..core import image_service

router = APIRouter(prefix="/assets", tags=["Assets"])

@router.get("/icons/{icon_name}")
def get_icon(icon_name: str, grayscale: bool = False):
    if ".." in icon_name or "/" in icon_name:
        raise HTTPException(status_code=400)
    image_buffer = image_service.process_image(icon_name, grayscale=grayscale)
    if image_buffer is None:
        raise HTTPException(status_code=404)
    return StreamingResponse(image_buffer, media_type="image/png")