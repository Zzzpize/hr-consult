from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..core.redis_client import redis_client

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest):
    """Аутентификация пользователя через Redis."""
    user = redis_client.get_user_by_username(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = int(user['id'])
    stored_password = redis_client.get_user_auth(user_id)


    if not stored_password or stored_password != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "success": True,
        "role": user.get('role'),
        "user_id": user_id,
        "name": user.get('name')
    }