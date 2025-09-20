# backend/app/api/gamification.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Set

router = APIRouter(
    prefix="/gamification",
    tags=["Gamification"]
)

class GamificationProgress(BaseModel):
    xp: int
    level: int
    achievements: Set[str]

class EventResponse(BaseModel):
    xp_added: int
    total_xp: int
    new_level: int
    unlocked_achievements: List[str]


@router.get("/progress/{user_id}", response_model=GamificationProgress)
def get_user_progress(user_id: int):
    """
    Возвращает игровой прогресс пользователя (заглушка).
    """
    return {
        "xp": 150,
        "level": 3,
        "achievements": {"profile_50", "first_plan"}
    }

@router.post("/event/{user_id}", response_model=EventResponse)
def trigger_event(user_id: int, event_key: str):
    """
    Обрабатывает игровое событие (заглушка).
    """
    if event_key == "SKILL_ADDED":
        return {
            "xp_added": 10,
            "total_xp": 160, 
            "new_level": 3, 
            "unlocked_achievements": []
        }

    if event_key == "PROFILE_100":
         return {
            "xp_added": 100,
            "total_xp": 250, 
            "new_level": 4, 
            "unlocked_achievements": ["PROFILE_MASTER"]
        }
    return {"xp_added": 0, "total_xp": 150, "new_level": 3, "unlocked_achievements": []}