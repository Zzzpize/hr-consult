from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
    Пока это демо!
    """
    if request.username == "admin" and request.password == "admin":
        return {"success": True, "role": "Admin", "user_id": 0, "name": "Администратор"}
    if request.username == "hr" and request.password == "hr":
        return {"success": True, "role": "HR", "user_id": 101, "name": "Петр Петров"}
    if request.username == "employee" and request.password == "employee":
        return {"success": True, "role": "Работник", "user_id": 1, "name": "Иван Иванов"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")