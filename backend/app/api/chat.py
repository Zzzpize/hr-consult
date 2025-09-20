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

class CareerPlanSaveRequest(BaseModel):
    user_id: int
    plan_data: Dict[str, Any]
    
@router.post("/message")
def handle_chat_message(request: ChatMessageRequest):
    """Принимает последнее сообщение пользователя и возвращает ответ бота."""
    try:
        bot_response = llm_service.get_next_chat_response(request.user_id, request.message)
        return {"response": bot_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.post("/generate-plan")
def generate_plan_and_update_profile(request: ChatPlanRequest):
    """
    Генерирует план, обновляет профиль на основе чата, но НЕ сохраняет сам план.
    """
    try:
        user_id = request.user_id
        history = redis_client.get_active_chat_history(user_id)
        if not history:
            raise HTTPException(status_code=404, detail="Активная история чата не найдена.")

        print(f"Extracting profile data for user {user_id} from chat...")
        extracted_data = llm_service.extract_profile_data_from_chat(history)
        if extracted_data:
            profile_update = {k: v for k, v in extracted_data.items() if k in ["name", "position", "about"] and v}
            if profile_update:
                redis_client.update_user_profile(user_id, profile_update)
            if extracted_data.get("skills"):
                redis_client.update_user_skills(user_id, extracted_data["skills"])
            print(f"Profile for user {user_id} updated with data: {extracted_data}")

        plan_json = llm_service.generate_final_plan_from_chat(user_id)
        
        return {"plan": plan_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-plan")
def save_career_plan(request: CareerPlanSaveRequest):
    """Сохраняет предоставленный карьерный план в Redis."""
    try:
        redis_client.save_career_plan(request.user_id, request.plan_data)
        return {"success": True, "message": "План успешно сохранен."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/history/{user_id}")
def get_chat_history(user_id: int):
    """Возвращает активную историю чата для пользователя."""
    history = redis_client.get_active_chat_history(user_id)
    return {"history": history}

@router.post("/generate-plan")
def generate_and_save_plan_from_chat(request: ChatPlanRequest):
    """
    Генерирует план на основе истории чата И СРАЗУ СОХРАНЯЕТ ЕГО в Redis.
    """
    try:
        plan_json = llm_service.generate_final_plan_from_chat(request.user_id)
        
        redis_client.save_career_plan(request.user_id, plan_json)

        return {"plan": plan_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/plans/{user_id}")
def get_all_plans_for_user(user_id: int):
    """Возвращает список всех сохраненных карьерных планов."""
    plans = redis_client.get_all_career_plans(user_id)
    return {"plans": plans}

@router.delete("/history/{user_id}")
def clear_chat_history(user_id: int):
    """Удаляет АКТИВНУЮ историю чата для пользователя."""
    redis_client.clear_active_chat_history(user_id)
    return {"success": True, "message": "Активная история чата очищена."}