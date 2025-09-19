import redis
import json
from typing import List, Dict, Optional, Any, Set

class RedisClient:
    def __init__(self, host='redis', port=6379, db=0):
        try:
            self.client = redis.Redis(
                host=host, port=port, db=db, decode_responses=True
            )
            self.client.ping()
            print("Successfully connected to Redis.")
        except redis.exceptions.ConnectionError as e:
            print(f"Error connecting to Redis: {e}")
            self.client = None

    # --- НОВЫЕ МЕТОДЫ ДЛЯ АУТЕНТИФИКАЦИИ ---
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Находит пользователя по его username/nickname."""
        if not self.client: return None
        
        user_id = self.client.hget("global:username_to_id", username)
        if not user_id:
            return None
        
        return self.get_user_profile(int(user_id))

    def get_user_auth(self, user_id: int) -> Optional[str]:
        """Получает пароль пользователя."""
        if not self.client: return None
        return self.client.get(f"user:{user_id}:auth")

    # --- МЕТОДЫ ДЛЯ УПРАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯМИ (обновленные) ---
    def create_user(self, name: str, role: str, username: str, password: str) -> Optional[int]:
        """Создает нового пользователя и все связанные с ним структуры."""
        if not self.client: return None
        
        # Проверяем, не занят ли username
        if self.client.hget("global:username_to_id", username):
            print(f"Username {username} already exists.")
            return None # Возвращаем None в случае ошибки

        user_id = self.client.incr("global:next_user_id")
        
        profile_data = {
            "id": user_id, "name": name, "role": role,
            "nickname": username, "photo_url": "", "about": ""
        }
        self.client.hset(f"user:{user_id}", mapping=profile_data)
        self.client.set(f"user:{user_id}:auth", password)
        self.client.hset(f"user:{user_id}:gamification", mapping={"xp": 0, "level": 1})
        self.client.hset("global:username_to_id", username, user_id)
        
        return user_id

    def get_all_users_info(self) -> List[Dict]:
        """Возвращает информацию о всех пользователях."""
        if not self.client: return []
        
        user_ids_map = self.client.hgetall("global:username_to_id")
        users_list = []
        for username, user_id in user_ids_map.items():
            user_data = self.get_user_profile(int(user_id))
            if user_data:
                users_list.append(user_data)
        return users_list

    def delete_user(self, user_id: int):
        """Полностью удаляет пользователя и все его данные."""
        if not self.client: return

        profile = self.get_user_profile(user_id)
        if profile and 'nickname' in profile:
            self.client.hdel("global:username_to_id", profile['nickname'])

        keys_to_delete = self.client.keys(f"user:{user_id}*")
        if keys_to_delete:
            self.client.delete(*keys_to_delete)

    # --- Методы для профиля пользователя ---
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Возвращает полный профиль пользователя."""
        if not self.client: return None
        return self.client.hgetall(f"user:{user_id}")

    def add_skill(self, user_id: int, skill: str):
        """Добавляет навык пользователю."""
        if not self.client: return
        self.client.sadd(f"user:{user_id}:skills", skill.lower())

    def get_user_skills(self, user_id: int) -> Set[str]:
        """Возвращает набор навыков пользователя."""
        if not self.client: return set()
        return self.client.smembers(f"user:{user_id}:skills")

    # --- Методы для Геймификации ---

    def get_gamification_stats(self, user_id: int) -> Dict:
        """Возвращает игровые статы пользователя."""
        if not self.client: return {"xp": 0, "level": 1}
        stats = self.client.hgetall(f"user:{user_id}:gamification")
        return {k: int(v) for k, v in stats.items()}

    def update_xp_and_level(self, user_id: int, new_xp: int, new_level: int):
        """Обновляет XP и уровень пользователя."""
        if not self.client: return
        self.client.hset(f"user:{user_id}:gamification", mapping={"xp": new_xp, "level": new_level})

    def add_achievement(self, user_id: int, achievement_id: str):
        """Добавляет достижение пользователю."""
        if not self.client: return
        self.client.sadd(f"user:{user_id}:achievements", achievement_id)

    def get_user_achievements(self, user_id: int) -> Set[str]:
        """Возвращает набор достижений пользователя."""
        if not self.client: return set()
        return self.client.smembers(f"user:{user_id}:achievements")

    # --- Методы для Эмбеддингов (ML) ---

    def save_user_embedding(self, user_id: int, embedding: List[float]):
        """Сохраняет эмбеддинг профиля пользователя."""
        if not self.client: return
        embedding_json = json.dumps(embedding)
        self.client.set(f"user:{user_id}:embedding", embedding_json)

    def get_user_embedding(self, user_id: int) -> Optional[List[float]]:
        """Извлекает и десериализует эмбеддинг пользователя."""
        if not self.client: return None
        embedding_json = self.client.get(f"user:{user_id}:embedding")
        if embedding_json:
            return json.loads(embedding_json)
        return None
    
    

redis_client = RedisClient()