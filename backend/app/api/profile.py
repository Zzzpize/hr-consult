from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..core.redis_client import redis_client

router = APIRouter(prefix="/profile", tags=["User Profile"])

class ProfileUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    about: Optional[str] = None
    skills: Optional[List[str]] = None

@router.put("/{user_id}")
def update_user_profile(user_id: int, profile_data: ProfileUpdateRequest):
    """Обновляет редактируемые поля профиля пользователя."""
    
    # Собираем данные для обновления основного хэша профиля
    update_data = {}
    if profile_data.nickname is not None:
        update_data['nickname'] = profile_data.nickname
    if profile_data.about is not None:
        update_data['about'] = profile_data.about
    
    if update_data:
        redis_client.update_user_profile(user_id, update_data)

    # Отдельно обновляем навыки, так как они хранятся в Set
    if profile_data.skills is not None:
        redis_client.update_user_skills(user_id, profile_data.skills)

    return {"success": True, "updated_user_id": user_id}