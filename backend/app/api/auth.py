from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..core.redis_client import redis_client
from ..core.config import ADMIN_PASSWORD, ADMIN_USERNAME


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest):
    """
    Аутентификация пользователя.
    Сначала проверяет на соответствие админу из .env,
    затем ищет обычного пользователя в Redis.
    """

    if request.username == ADMIN_USERNAME and request.password == ADMIN_PASSWORD:
        admin_profile = redis_client.get_user_by_username(ADMIN_USERNAME)
        if admin_profile:
            return {
                "success": True,
                "role": "Admin",
                "user_id": int(admin_profile.get('id', 0)),
                "name": admin_profile.get('name', 'Администратор')
            }
        else:
            return {
                "success": True,
                "role": "Admin",
                "user_id": 0,
                "name": "Администратор"
            }

    user = redis_client.get_user_by_username(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = int(user['id'])
    stored_password = redis_client.get_user_auth(user_id)

    if not stored_password or stored_password != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.get('role') == 'Admin':
        raise HTTPException(status_code=403, detail="Access denied for this role via regular login.")

    return {
        "success": True,
        "role": user.get('role'),
        "user_id": user_id,
        "name": user.get('name')
    }