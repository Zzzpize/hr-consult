from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from ..services import llm_service
from ..core.redis_client import redis_client

router = APIRouter(prefix="/chat", tags=["AI Chat Consultant"])

class ChatMessageRequest(BaseModel):
    user_id: int
    message: str

class ChatPlanRequest(BaseModel):
    user_id: int

@router.post("/message")
def handle_chat_message(request: ChatMessageRequest):
    """Принимает последнее сообщение пользователя и возвращает ответ бота."""
    try:
        bot_response = llm_service.get_next_chat_response(request.user_id, request.message)
        return {"response": bot_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-plan")
def generate_plan_from_chat(request: ChatPlanRequest):
    """Принимает user_id и генерирует JSON-план на основе истории чата."""
    try:
        plan_json = llm_service.generate_final_plan_from_chat(request.user_id)
        return {"plan": plan_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
def get_chat_history(user_id: int):
    """Возвращает сохраненную историю чата для пользователя."""
    history = redis_client.get_chat_history(user_id)
    return {"history": history}