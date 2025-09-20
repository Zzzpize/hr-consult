import requests
import streamlit as st
from typing import List, Dict, Any, Optional

BASE_URL = "http://backend:8000"

def _handle_request_errors(request_func):
    def wrapper(*args, **kwargs):
        try:
            response = request_func(*args, **kwargs)
            if response.status_code >= 400:
                error_details = response.json().get('detail', 'Неизвестная ошибка сервера')
                st.error(f"Ошибка API (статус {response.status_code}): {error_details}")
                return None
            return response.json()
        except requests.exceptions.ConnectionError:
            st.error("Ошибка подключения к серверу API. Убедитесь, что бэкенд-сервис запущен и доступен.")
            return None
        except Exception as e:
            st.error(f"Произошла непредвиденная ошибка: {e}")
            return None
    return wrapper

# --- Authentication ---
@_handle_request_errors
def login(username: str, password: str) -> Optional[Dict[str, Any]]:
    response = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
    return response

# --- Users & Admin ---
@_handle_request_errors
def get_all_users() -> Optional[List[Dict[str, Any]]]:
    response = requests.get(f"{BASE_URL}/users/")
    return response

@_handle_request_errors
def create_user(name: str, role: str, username: str, password: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Создает нового пользователя. Пароль необязателен.
    Если password is None, бэкенд сгенерирует его сам.
    """
    payload = {
        "name": name,
        "role": role,
        "username": username,
    }
    if password:
        payload["password"] = password
    
    response = requests.post(f"{BASE_URL}/users/", json=payload)
    return response

@_handle_request_errors
def delete_user(user_id: int) -> Optional[Dict[str, Any]]:
    response = requests.delete(f"{BASE_URL}/users/{user_id}")
    return response

@_handle_request_errors
def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    response = requests.get(f"{BASE_URL}/users/{user_id}/profile")
    return response
'''
# --- Career Plan AI ---
@_handle_request_errors
def generate_career_plan(user_id: int) -> Optional[Dict[str, Any]]:
    response = requests.post(f"{BASE_URL}/career-plan/", json={"user_id": user_id})
    return response
'''
# --- Candidate Matching AI ---
@_handle_request_errors
def match_candidates(prompt: str) -> Optional[List[Dict[str, Any]]]:
    response = requests.post(f"{BASE_URL}/matching/candidates", json={"prompt": prompt})
    return response

# --- Gamification ---
@_handle_request_errors
def get_user_progress(user_id: int) -> Optional[Dict[str, Any]]:
    response = requests.get(f"{BASE_URL}/gamification/progress/{user_id}")
    return response

@_handle_request_errors
def trigger_gamification_event(user_id: int, event_key: str) -> Optional[Dict[str, Any]]:
    response = requests.post(f"{BASE_URL}/gamification/event/{user_id}", params={"event_key": event_key})
    return response

@_handle_request_errors
def create_offer(from_hr_id: int, to_user_id: int, title: str, description: str) -> Optional[Dict[str, Any]]:
    """Создает новый оффер."""
    payload = {
        "from_hr_id": from_hr_id, "to_user_id": to_user_id,
        "title": title, "description": description
    }
    response = requests.post(f"{BASE_URL}/offers/", json=payload)
    return response

@_handle_request_errors
def get_user_offers(user_id: int) -> Optional[List[Dict[str, Any]]]:
    """Получает офферы для сотрудника."""
    response = requests.get(f"{BASE_URL}/offers/user/{user_id}")
    return response

@_handle_request_errors
def get_hr_offers(hr_id: int) -> Optional[List[Dict[str, Any]]]:
    """Получает офферы, отправленные HR."""
    response = requests.get(f"{BASE_URL}/offers/hr/{hr_id}")
    return response

@_handle_request_errors
def update_offer_status(offer_id: int, status: str) -> Optional[Dict[str, Any]]:
    """Обновляет статус оффера."""
    response = requests.put(f"{BASE_URL}/offers/{offer_id}/status", json={"status": status})
    return response

@_handle_request_errors
def get_user_skills(user_id: int) -> Optional[List[str]]:
    """Получает список навыков пользователя."""
    profile = get_user_profile(user_id)
    return profile.get('skills', []) if profile else []

@_handle_request_errors
def update_user_profile(user_id: int, nickname: str, about: str, skills: List[str]) -> Optional[Dict[str, Any]]:
    """Обновляет профиль пользователя."""
    payload = {"nickname": nickname, "about": about, "skills": skills}
    response = requests.put(f"{BASE_URL}/profile/{user_id}", json=payload)
    return response

@_handle_request_errors
def get_chat_history(user_id: int) -> Optional[Dict]:
    """Получает историю чата для пользователя."""
    return requests.get(f"{BASE_URL}/chat/history/{user_id}")

@_handle_request_errors
def get_chat_response(user_id: int, message: str) -> Optional[Dict]:
    """Отправляет сообщение в чат и получает ответ бота."""
    return requests.post(f"{BASE_URL}/chat/message", json={"user_id": user_id, "message": message})

@_handle_request_errors
def generate_final_plan_from_chat(user_id: int) -> Optional[Dict]:
    """Отправляет запрос на генерацию финального плана на основе истории чата."""
    return requests.post(f"{BASE_URL}/chat/generate-plan", json={"user_id": user_id})

@_handle_request_errors
def get_all_career_plans(user_id: int) -> Optional[Dict]:
    """Получает все сохраненные карьерные планы."""
    return requests.get(f"{BASE_URL}/chat/plans/{user_id}")

