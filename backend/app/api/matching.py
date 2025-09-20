from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from ..services import llm_service
from ..core.redis_client import redis_client

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
    score: float

@router.post("/candidates", response_model=List[MatchResult])
def match_candidates(request: MatchRequest):
    """Подбирает кандидатов, используя ML-сервис."""
    
    similar_users = llm_service.find_similar_users(request.prompt)

    results = []
    for user_match in similar_users:
        profile = redis_client.get_user_profile(user_match['user_id'])
        if profile:
            results.append({
                "user_id": profile['id'],
                "name": profile.get('name', 'N/A'),
                "position": profile.get('position', 'N/A'),
                "score": user_match['score']
            })
    
    return results

@router.post("/vectorize-all")
def vectorize_all_users():
    """Запускает процесс векторизации всех пользователей в базе."""
    try:
        llm_service.vectorize_all_users_in_redis()
        return {"status": "ok", "message": "Процесс векторизации запущен."}
    except Exception as e:
        return {"status": "error", "message": str(e)}