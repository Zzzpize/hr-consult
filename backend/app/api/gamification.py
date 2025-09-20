from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from ..services.gamification_service import gamification_service
from ..core.redis_client import redis_client
from ..services.gamification_config import ACHIEVEMENTS

router = APIRouter(prefix="/gamification", tags=["Gamification"])

class EventRequest(BaseModel):
    event_key: str
    event_data: Dict[str, Any] = {}

@router.get("/progress/{user_id}")
def get_user_progress(user_id: int):
    """
    Возвращает игровой прогресс пользователя (XP и уровень).
    """
    stats = redis_client.get_gamification_stats(user_id)
    if not stats:
        return {"xp": 0, "level": 1}
    return stats


@router.post("/event/{user_id}")
def trigger_event(user_id: int, request: EventRequest):
    """
    Принимает игровое событие и обрабатывает его.
    """
    return gamification_service.process_event(
        user_id, request.event_key, request.event_data
    )

@router.get("/achievements/{user_id}")
def get_user_achievements_status(user_id: int):
    """
    Возвращает полный список всех достижений и статус их получения для пользователя.
    """
    unlocked_keys = redis_client.get_user_achievements(user_id)
    all_achievements_status = []
    
    for key, data in ACHIEVEMENTS.items():
        all_achievements_status.append({
            "key": key,
            "name": data["name"],
            "description": data["description"],
            "icon": data["icon"],
            "unlocked": key in unlocked_keys
        })
        
    return {"achievements": all_achievements_status}