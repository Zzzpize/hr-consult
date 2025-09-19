import redis
import json
from typing import List, Dict, Optional, Set

class RedisClient:
    """
    Централизованный клиент для работы с Redis, инкапсулирующий всю логику
    доступа к данным согласно принятой архитектуре.
    """
    def __init__(self, host='redis', port=6379, db=0):
        """
        Инициализирует подключение к Redis.
        Имя хоста 'redis' будет работать внутри Docker Compose.
        """
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True # автоматически декодирует ответы из bytes в str
            )
            # Проверяем соединение
            self.client.ping()
            print("Successfully connected to Redis.")
        except redis.exceptions.ConnectionError as e:
            print(f"Error connecting to Redis: {e}")
            self.client = None

    # --- Методы для Админки и Управления Пользователями ---

    def create_user(self, name: str, role: str, password: str = "password") -> Optional[int]:
        """Создает нового пользователя и все связанные с ним структуры."""
        if not self.client: return None

        user_id = self.client.incr("global:next_user_id")
        
        self.client.hset(f"user:{user_id}", mapping={
            "id": user_id,
            "name": name,
            "role": role,
            "nickname": f"user{user_id}",
            "photo_url": "",
            "about": ""
        })

        self.client.set(f"user:{user_id}:auth", password)

        self.client.hset(f"user:{user_id}:gamification", mapping={"xp": 0, "level": 1})


        self.client.sadd(f"user:{user_id}:skills", "dummy")
        self.client.srem(f"user:{user_id}:skills", "dummy")

        self.client.sadd(f"user:{user_id}:achievements", "dummy")
        self.client.srem(f"user:{user_id}:achievements", "dummy")

        self.client.hset("global:username_to_id", f"user{user_id}", user_id)

        return user_id

    def get_all_users_info(self) -> List[Dict]:
        """Возвращает краткую информацию о всех пользователях."""
        if not self.client: return []

        user_ids = [key.split(':')[1] for key in self.client.scan_iter("user:*:gamification")]
        
        users_list = []
        for user_id in user_ids:
            user_data = self.client.hgetall(f"user:{user_id}")
            if user_data:
                users_list.append(user_data)
        return users_list

    def delete_user(self, user_id: int):
        """Полностью удаляет пользователя и все его данные."""
        if not self.client: return

        keys_to_delete = self.client.keys(f"user:{user_id}*")
        if keys_to_delete:
            self.client.delete(*keys_to_delete)

        profile = self.client.hgetall(f"user:{user_id}")
        if profile and 'nickname' in profile:
            self.client.hdel("global:username_to_id", profile['nickname'])

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