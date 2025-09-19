# backend/app/api/matching.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(
    prefix="/matching",
    tags=["Candidate Matching AI"]
)

class MatchRequest(BaseModel):
    prompt: str

class MatchResult(BaseModel):
    user_id: int
    name: str
    position: str
    score: float # от 0 до 1

@router.post("/candidates", response_model=List[MatchResult])
def match_candidates(request: MatchRequest):
    """
    Подбирает кандидатов по текстовому промпту (заглушка).
    Возвращает жестко закодированный список подходящих сотрудников.
    """
    # промпт был "ищу опытного питониста"
    return [
        {
            "user_id": 1,
            "name": "Иван Иванов",
            "position": "Junior Python Developer",
            "score": 0.92
        },
        {
            "user_id": 5, # Несуществующий для простоты
            "name": "Сергей Васильев",
            "position": "Python Developer",
            "score": 0.87
        },
        {
            "user_id": 2,
            "name": "Анна Сидорова",
            "position": "Frontend Developer",
            "score": 0.65 # Нашлась, потому что у нее в опыте был Python-проект
        }
    ]