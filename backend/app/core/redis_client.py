import redis
import json
from typing import List, Dict, Optional, Any, Set
from datetime import datetime

class RedisClient:
    """
    Централизованный клиент для работы с Redis, инкапсулирующий всю логику
    доступа к данным согласно принятой архитектуре.
    """
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

    # --- Методы для Аутентификации ---
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Находит пользователя по его username/nickname."""
        if not self.client: return None
        user_id = self.client.hget("global:username_to_id", username)
        return self.get_user_profile(int(user_id)) if user_id else None

    def get_user_auth(self, user_id: int) -> Optional[str]:
        """Получает пароль пользователя."""
        if not self.client: return None
        return self.client.get(f"user:{user_id}:auth")

    # --- Методы для Управления Пользователями ---
    def create_user(self, name: str, role: str, username: str, password: str) -> Optional[int]:
        """Создает нового пользователя и все связанные с ним структуры."""
        if not self.client: return None
        if self.client.hget("global:username_to_id", username):
            return None
        user_id = self.client.incr("global:next_user_id")
        profile_data = {"id": user_id, "name": name, "role": role, "nickname": username, "photo_url": "", "about": ""}
        self.client.hset(f"user:{user_id}", mapping=profile_data)
        self.client.set(f"user:{user_id}:auth", password)
        self.client.hset(f"user:{user_id}:gamification", mapping={"xp": 0, "level": 1})
        self.client.hset("global:username_to_id", username, user_id)
        return user_id

    def get_all_users_info(self) -> List[Dict]:
        """Возвращает информацию о всех пользователях."""
        if not self.client: return []
        user_ids_map = self.client.hgetall("global:username_to_id")
        users_list = [self.get_user_profile(int(uid)) for uname, uid in user_ids_map.items()]
        return [user for user in users_list if user]

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
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает основной профиль пользователя (Hash)."""
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

    # --- Методы для Геймификации (ВОЗВРАЩЕНЫ) ---
    def get_gamification_stats(self, user_id: int) -> Dict:
        """Возвращает игровые статы пользователя."""
        if not self.client: return {"xp": 0, "level": 1}
        stats = self.client.hgetall(f"user:{user_id}:gamification")
        return {k: int(v) for k, v in stats.items()} if stats else {"xp": 0, "level": 1}

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

    # --- Методы для Эмбеддингов (ML) (ВОЗВРАЩЕНЫ) ---
    def save_user_embedding(self, user_id: int, embedding: List[float]):
        """Сохраняет эмбеддинг профиля пользователя."""
        if not self.client: return
        embedding_json = json.dumps(embedding)
        self.client.set(f"user:{user_id}:embedding", embedding_json)

    def get_user_embedding(self, user_id: int) -> Optional[List[float]]:
        """Извлекает и десериализует эмбеддинг пользователя."""
        if not self.client: return None
        embedding_json = self.client.get(f"user:{user_id}:embedding")
        return json.loads(embedding_json) if embedding_json else None

    # --- Методы для Офферов ---
    def create_offer(self, from_hr_id: int, to_user_id: int, title: str, description: str) -> int:
        """Создает новый оффер и связывает его с HR и сотрудником."""
        if not self.client: return 0
        offer_id = self.client.incr("global:next_offer_id")
        
        offer_key = f"offer:{offer_id}"
        offer_data = {
            "id": offer_id,
            "from_hr_id": from_hr_id,
            "to_user_id": to_user_id,
            "title": title,
            "description": description,
            "status": "Отправлено",
            "timestamp": json.dumps(datetime.now(), default=str)
        }
        self.client.hset(offer_key, mapping=offer_data)

        self.client.lpush(f"user:{to_user_id}:offers_received", offer_id)
        self.client.lpush(f"user:{from_hr_id}:offers_sent", offer_id)
        
        return offer_id

    def get_offer_by_id(self, offer_id: int) -> Optional[Dict[str, Any]]:
        """Получает детали оффера по его ID."""
        if not self.client: return None
        return self.client.hgetall(f"offer:{offer_id}")

    def get_user_offers(self, user_id: int) -> List[Dict[str, Any]]:
        """Получает все офферы, отправленные сотруднику."""
        if not self.client: return []
        offer_ids = self.client.lrange(f"user:{user_id}:offers_received", 0, -1)
        offers = [self.get_offer_by_id(int(oid)) for oid in offer_ids]
        return [offer for offer in offers if offer]

    def get_hr_sent_offers(self, hr_id: int) -> List[Dict[str, Any]]:
        """Получает все офферы, отправленные HR-специалистом."""
        if not self.client: return []
        offer_ids = self.client.lrange(f"user:{hr_id}:offers_sent", 0, -1)
        offers = [self.get_offer_by_id(int(oid)) for oid in offer_ids]
        return [offer for offer in offers if offer]

    def update_offer_status(self, offer_id: int, new_status: str):
        """Обновляет статус оффера."""
        if not self.client: return
        self.client.hset(f"offer:{offer_id}", "status", new_status)
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]):
        """Обновляет поля в профиле пользователя."""
        if not self.client: return
        self.client.hset(f"user:{user_id}", mapping=profile_data)

    def update_user_skills(self, user_id: int, skills: List[str]):
        """Полностью заменяет список навыков пользователя."""
        if not self.client: return
        key = f"user:{user_id}:skills"
        self.client.delete(key)
        if skills:
            self.client.sadd(key, *skills)

    # --- Методы для Диалоговой Системы ---
    def get_chat_history(self, user_id: int) -> List[Dict]:
        """Получает историю чата из Redis List."""
        if not self.client: return []
        history_json = self.client.lrange(f"user:{user_id}:chat_history", 0, -1)
        return [json.loads(msg) for msg in history_json]

    def add_message_to_history(self, user_id: int, message: Dict):
        """Добавляет новое сообщение в историю чата."""
        if not self.client: return
        self.client.lpush(f"user:{user_id}:chat_history", json.dumps(message))

    def get_dialog_state(self, user_id: int) -> Dict:
        """Получает состояние анкеты-диалога."""
        if not self.client: return {}
        state = self.client.hgetall(f"user:{user_id}:dialog_state")
        return {k: v.lower() == 'true' for k, v in state.items()}

    def update_dialog_state(self, user_id: int, key: str, value: bool):
        """Обновляет состояние анкеты-диалога."""
        if not self.client: return
        self.client.hset(f"user:{user_id}:dialog_state", key, str(value).lower())

    def save_career_plan(self, user_id: int, plan_data: Dict) -> None:
        """Сохраняет один карьерный план для пользователя."""
        if not self.client: return
        self.client.rpush(f"user:{user_id}:career_plans", json.dumps(plan_data))

    def get_all_career_plans(self, user_id: int) -> List[Dict]:
        """Получает все сохраненные карьерные планы для пользователя."""
        if not self.client: return []
        plans_json = self.client.lrange(f"user:{user_id}:career_plans", 0, -1)
        return [json.loads(p) for p in plans_json]


redis_client = RedisClient()