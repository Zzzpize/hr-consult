# backend/app/api/career_plan.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter(
    prefix="/career-plan",
    tags=["Career Plan AI"]
)

class CareerPlanRequest(BaseModel):
    # TODO доп параметры
    user_id: int

@router.post("/")
def generate_career_plan(request: CareerPlanRequest):
    """
    Генерирует карьерный план для пользователя (заглушка).
    Возвращает заранее подготовленный JSON.
    """
    return {
        "current_analysis": "Ты отличный разработчик. Твои навыки в Python впечатляют. Твой опыт в проекте 'Альфа' показывает, что ты умеешь работать с high-load системами.",
        "recommended_path": {
            "target_role": "Middle+ Python Developer",
            "why_it_fits": "Это логичный следующий шаг, который позволит углубить твои технические знания и подготовит к будущему тимлидству."
        },
        "skill_gap": [
            {"skill": "Docker & Kubernetes", "reason": "Ключевая технология для наших новых сервисов, обязательна для Middle+ уровня."},
            {"skill": "Асинхронное программирование (asyncio)", "reason": "Позволит писать более производительный код для высоконагруженных частей системы."}
        ],
        "actionable_steps": [
            {"step": 1, "type": "Обучение", "description": "Пройди внутренний курс 'DevOps для разработчиков' на нашем портале."},
            {"step": 2, "type": "Проектная задача", "description": "Попроси у своего тимлида задачу по настройке CI/CD для вашего сервиса."},
            {"step": 3, "type": "Менторство", "description": "Найди ментора из DevOps-отдела. Мы рекомендуем Ивана Петрова."}
        ]
    }