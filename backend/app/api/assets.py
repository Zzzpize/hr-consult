from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from ..core import image_service
import os

router = APIRouter(prefix="/assets", tags=["Assets"])

ICON_BASE_PATH = "frontend/icons"

@router.get("/icons/{icon_name}")
def get_icon(icon_name: str, grayscale: bool = False):
    """
    Возвращает файл иконки, опционально в черно-белом варианте.
    """
    if ".." in icon_name or "/" in icon_name:
        raise HTTPException(status_code=400, detail="Invalid icon name")

    image_path = os.path.join(ICON_BASE_PATH, icon_name)
    
    image_buffer = image_service.process_image(image_path, grayscale=grayscale)

    if image_buffer is None:
        raise HTTPException(status_code=404, detail="Icon not found")
    
    return StreamingResponse(image_buffer, media_type="image/png")