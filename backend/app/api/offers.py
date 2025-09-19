# backend/app/api/offers.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from ..core.redis_client import redis_client

router = APIRouter(prefix="/offers", tags=["Offers"])

class OfferCreateRequest(BaseModel):
    from_hr_id: int
    to_user_id: int
    title: str
    description: str

class OfferStatusUpdateRequest(BaseModel):
    status: str

@router.post("/")
def create_offer(offer_data: OfferCreateRequest):
    """Создает новый оффер."""
    offer_id = redis_client.create_offer(
        from_hr_id=offer_data.from_hr_id,
        to_user_id=offer_data.to_user_id,
        title=offer_data.title,
        description=offer_data.description
    )
    return {"success": True, "offer_id": offer_id}

@router.get("/user/{user_id}", response_model=List[Dict[str, Any]])
def get_offers_for_user(user_id: int):
    """Получает все офферы для указанного сотрудника."""
    return redis_client.get_user_offers(user_id)

@router.get("/hr/{hr_id}", response_model=List[Dict[str, Any]])
def get_offers_from_hr(hr_id: int):
    """Получает все офферы, отправленные указанным HR."""
    return redis_client.get_hr_sent_offers(hr_id)

@router.put("/{offer_id}/status")
def update_offer_status(offer_id: int, request: OfferStatusUpdateRequest):
    """Обновляет статус оффера (например, на 'Принято' или 'Отклонено')."""
    redis_client.update_offer_status(offer_id, request.status)
    return {"success": True, "offer_id": offer_id, "new_status": request.status}