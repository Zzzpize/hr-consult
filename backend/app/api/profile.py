from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..core.redis_client import redis_client
from ..services import llm_service

router = APIRouter(prefix="/profile", tags=["User Profile"])

class ProfileUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    about: Optional[str] = None
    skills: Optional[List[str]] = None

@router.put("/{user_id}")
def update_user_profile(user_id: int, profile_data: ProfileUpdateRequest):
    """Обновляет редактируемые поля профиля пользователя."""

    update_data = {}
    if profile_data.nickname is not None:
        update_data['nickname'] = profile_data.nickname
    if profile_data.about is not None:
        update_data['about'] = profile_data.about
    
    if update_data:
        redis_client.update_user_profile(user_id, update_data)

    if profile_data.skills is not None:
        redis_client.update_user_skills(user_id, profile_data.skills)

    return {"success": True, "updated_user_id": user_id}

@router.post("/{user_id}/import-from-chat")
def import_data_from_chat(user_id: int):
    """
    Извлекает данные из активного чата и обновляет профиль пользователя.
    """
    history = redis_client.get_active_chat_history(user_id)
    if not history:
        raise HTTPException(status_code=404, detail="Активная история чата не найдена.")

    extracted_data = llm_service.extract_profile_data_from_chat(history)
    
    if not extracted_data:
        raise HTTPException(status_code=500, detail="Не удалось извлечь данные из диалога.")

    profile_update = {}
    if extracted_data.get("name"):
        profile_update["name"] = extracted_data["name"]
    if extracted_data.get("position"):
        profile_update["position"] = extracted_data["position"]
    if extracted_data.get("about"):
        profile_update["about"] = extracted_data["about"]
    
    if profile_update:
        redis_client.update_user_profile(user_id, profile_update)

    if extracted_data.get("skills"):
        redis_client.update_user_skills(user_id, extracted_data["skills"])
        
    return {"success": True, "imported_data": extracted_data}