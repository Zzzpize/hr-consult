import requests
import streamlit as st
from typing import List, Dict, Any, Optional


BASE_URL = "http://backend:8000"

# --- Вспомогательная функция для обработки ошибок ---
def _handle_request_errors(request_func):
    """
    Декоратор для централизованной обработки ошибок подключения и HTTP-статусов.
    """
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
    """Отправляет запрос на аутентификацию."""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    return response

# --- Users & Admin ---

@_handle_request_errors
def get_all_users() -> Optional[List[Dict[str, Any]]]:
    """Получает список всех пользователей для админ-панели."""
    response = requests.get(f"{BASE_URL}/users/")
    return response

@_handle_request_errors
def create_user(name: str, role: str) -> Optional[Dict[str, Any]]:
    """Отправляет запрос на создание нового пользователя."""
    response = requests.post(
        f"{BASE_URL}/users/",
        json={"name": name, "role": role}
    )
    return response

@_handle_request_errors
def delete_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Отправляет запрос на удаление пользователя."""
    response = requests.delete(f"{BASE_URL}/users/{user_id}")
    return response

@_handle_request_errors
def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """Получает детальную информацию о профиле пользователя."""
    response = requests.get(f"{BASE_URL}/users/{user_id}/profile")
    return response

# --- Career Plan AI ---

@_handle_request_errors
def generate_career_plan(user_id: int) -> Optional[Dict[str, Any]]:
    """Запрашивает генерацию карьерного плана для пользователя."""
    response = requests.post(
        f"{BASE_URL}/career-plan/",
        json={"user_id": user_id}
    )
    return response

# --- Candidate Matching AI ---

@_handle_request_errors
def match_candidates(prompt: str) -> Optional[List[Dict[str, Any]]]:
    """Запрашивает подбор кандидатов по текстовому описанию."""
    response = requests.post(
        f"{BASE_URL}/matching/candidates",
        json={"prompt": prompt}
    )
    return response

# --- Gamification ---

@_handle_request_errors
def get_user_progress(user_id: int) -> Optional[Dict[str, Any]]:
    """Получает игровой прогресс пользователя (XP, уровень, ачивки)."""
    response = requests.get(f"{BASE_URL}/gamification/progress/{user_id}")
    return response

@_handle_request_errors
def trigger_gamification_event(user_id: int, event_key: str) -> Optional[Dict[str, Any]]:
    """Сообщает бэкенду о произошедшем игровом событии."""
    response = requests.post(
        f"{BASE_URL}/gamification/event/{user_id}",
        params={"event_key": event_key} 
    )
    return response
    