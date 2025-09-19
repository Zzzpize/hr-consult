from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import secrets
import string
from ..core.redis_client import redis_client

router = APIRouter(prefix="/users", tags=["Users & Admin"])

# --- Вспомогательная функция для генерации пароля ---
def generate_password(length: int = 8) -> str:
    """Генерирует простой пароль из букв и цифр."""
    alphabet = string.ascii_letters + string.digits # Убрали спецсимволы
    return ''.join(secrets.choice(alphabet) for i in range(length))

class UserCreateRequest(BaseModel):
    name: str
    role: str
    username: str
    password: Optional[str] = None

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_users():
    """Возвращает список всех пользователей из Redis, ИСКЛЮЧАЯ админа."""
    all_users = redis_client.get_all_users_info()
    # Фильтруем список, чтобы не показывать админа в админке
    return [user for user in all_users if user.get("role") != "Admin"]

@router.post("/")
def create_user(user_data: UserCreateRequest):
    """Создает нового пользователя в Redis. Генерирует пароль, если он не предоставлен."""
    password_to_set = user_data.password if user_data.password else generate_password()
    user_id = redis_client.create_user(
        name=user_data.name, role=user_data.role,
        username=user_data.username, password=password_to_set
    )
    if user_id is None:
        raise HTTPException(status_code=409, detail=f"Username '{user_data.username}' already exists")
    
    return {
        "success": True, "user_id": user_id,
        "name": user_data.name, "role": user_data.role,
        "generated_password": password_to_set
    }

@router.delete("/{user_id}")
def delete_user(user_id: int):
    """Удаляет пользователя из Redis, с защитой от удаления админа."""
    user_to_delete = redis_client.get_user_profile(user_id)
    if user_to_delete and user_to_delete.get("role") == "Admin":
        raise HTTPException(status_code=403, detail="Cannot delete the admin user.")
    
    redis_client.delete_user(user_id)
    return {"success": True, "deleted_user_id": user_id}

@router.get("/{user_id}/profile")
def get_user_profile(user_id: int):
    """Возвращает детальный профиль пользователя из Redis."""
    profile = redis_client.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    if 'skills' not in profile:
        profile['skills'] = ["python", "fastapi", "docker"]
    if 'photo_url' not in profile or not profile['photo_url']:
        profile['photo_url'] = f"https://i.pravatar.cc/150?u={user_id}" 
    
    return profile