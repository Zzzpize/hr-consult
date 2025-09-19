# backend/app/api/users.py
from fastapi import APIRouter
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter(
    prefix="/users",
    tags=["Users & Admin"]
)

# --- Фейковая база данных для заглушек ---
FAKE_USERS_DB = [
    {"id": 1, "name": "Иван Иванов", "role": "Работник", "position": "Junior Python Developer"},
    {"id": 2, "name": "Анна Сидорова", "role": "Работник", "position": "Frontend Developer"},
    {"id": 101, "name": "Петр Петров", "role": "HR", "position": "HR Manager"},
]
# --- Конец фейковой базы ---

class UserCreateRequest(BaseModel):
    name: str
    role: str

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_users():
    """Возвращает список всех пользователей для админ-панели."""
    return FAKE_USERS_DB

@router.post("/")
def create_user(user_data: UserCreateRequest):
    """Создает нового пользователя (симуляция)."""
    new_id = max(u["id"] for u in FAKE_USERS_DB) + 1
    return {"success": True, "user_id": new_id, "name": user_data.name, "role": user_data.role}

@router.delete("/{user_id}")
def delete_user(user_id: int):
    """Удаляет пользователя (симуляция)."""
    return {"success": True, "deleted_user_id": user_id}

@router.get("/{user_id}/profile")
def get_user_profile(user_id: int):
    """Возвращает детальный профиль пользователя."""
    if user_id == 1:
        return {
            "id": 1,
            "name": "Иван Иванов",
            "nickname": "ivan.dev",
            "position": "Junior Python Developer",
            "photo_url": "https://i.pravatar.cc/150?img=68",
            "about": "Увлеченный бэкенд-разработчик, люблю чистый код и решать сложные задачи. В свободное время играю на гитаре.",
            "skills": ["python", "fastapi", "sql", "git"],
            "career_path_visible": True,
            "level_visible": True,
            "achievements_visible": True
        }
    return {"detail": "User not found"}