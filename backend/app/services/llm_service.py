from typing import Dict
from ..core.redis_client import redis_client
from openai import OpenAI

API_KEY = "sk-LqCf11ej9dj70ObUG956eQ"
BASE_URL = "https://llm.t1v.scibox.tech/v1"

system_prompt_info = "Ты — дружелюбный и эмпатичный карьерный консультант 'Навигатор'. Твоя цель — узнать его 1) ФИО 2) отдел, должность и стаж работы 3) навыки (hard и soft skills) 4) последние 2 реализованных проекта 5) амбиции (вакансия, на которую хочет попасть пользователь). Вся уже собранная информация будет прикреплена последним абзацем в виде словаря (тебя будут интересовать элементы с ключом 'role' = 'user'). Если ты видишь, что не все 5 пунктов закрыты полностью – задаешь пользователю уточняющие вопросы до тех пор, пока не соберется полная база знаний. Как только ты понимаешь, что база знаний полна информации по всем 5 пунктам – предложи пользователю заполнить его профиль автоматически. Будь вежливым, но не жеманным и льстительным. При необходимости обращайся по имени (если ты его уже знаешь). Вот текущая история общения с пользователем, где ты можешь найти информацию о нем:\n"

system_prompt_analyze = "Ты — дружелюбный и эмпатичный карьерный консультант 'Навигатор'. Твоя цель — построить последовательный карьерный план на основании известной о пользователе информации. Вся уже собранная информация будет прикреплена последним абзацем в виде словаря (тебя будут интересовать элементы с ключом 'role' = 'user'). Будь вежливым, но не жеманным и льстительным. При необходимости обращайся по имени. Вот текущая история общения с пользователем, где ты можешь найти информацию о нем:\n"

example_plan = {
  "plan_id": "plan_1726834988_user_3", 
  "created_at": "...",
  "plan_title": "Ваш карьерный путь к Middle Python Developer", 
  "current_analysis": "Вы являетесь уверенным Junior Python разработчиком с хорошим пониманием FastAPI и SQL. Ваш опыт в проекте 'Альфа' показывает, что вы способны самостоятельно решать задачи. Основная зона роста - работа с инфраструктурой и более сложными архитектурными паттернами.",
  "recommended_path": {
    "target_role": "Middle Python Developer",
    "why_it_fits": "Эта роль является логичным следующим шагом, соответствующим вашим амбициям стать тимлидом. Она позволит углубить технические знания, взять на себя больше ответственности и подготовиться к менторству."
  },
  "skill_gap": [
    {
      "skill": "Docker & Kubernetes",
      "reason": "Ключевая технология для развертывания и масштабирования наших сервисов, обязательна для Middle+ уровня."
    },
    {
      "skill": "Асинхронное программирование (asyncio)",
      "reason": "Позволит вам писать более производительный код для высоконагруженных частей системы, что критично для проекта 'Омега'."
    },
    {
      "skill": "Unit-тестирование (pytest)",
      "reason": "Написание надежных тестов - признак зрелого разработчика, это повысит качество и стабильность кода."
    }
  ],
  "actionable_steps": [
    {
      "step": 1,
      "type": "Обучение",
      "description": "Пройдите внутренний курс 'DevOps для разработчиков' на нашем корпоративном портале.",
      "timeline": "1-2 месяца"
    },
    {
      "step": 2,
      "type": "Практика",
      "description": "Попросите у своего тимлида задачу по настройке CI/CD для вашего текущего сервиса с использованием GitLab CI.",
      "timeline": "Следующий квартал"
    },
    {
      "step": 3,
      "type": "Менторство",
      "description": "Найдите ментора из DevOps-отдела. Мы рекомендуем связаться с Иваном Петровым.",
      "timeline": "Постоянно"
    }
  ]
}

system_prompt_plan = "Вычлени из данного ответа всю необходимую информацию, чтобы полностью заполнить все поля, как в данном примере:\n{example_plan}\nВерни мне одной строкой аналогичный json-подобный объект, без лишних комментариев\n"

def exchange(system_prompt: str, user_text: str, temperature: float = 0.8, max_tokens: int = 400):
    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        resp = client.chat.completions.create(
            model = "Qwen2.5-72B-Instruct-AWQ",
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature = temperature,
            max_tokens = max_tokens,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"\n--- ПРОИЗОШЛА ОШИБКА ---\n{e}"
    
def get_next_chat_response(user_id: int, user_prompt: str) -> str:
    history = redis_client.get_dialog_state(user_id)
    redis_client.add_message_to_history(user_id, {"role": "user", "content": user_prompt})
    answer = exchange(system_prompt_info + history, user_prompt)
    redis_client.add_message_to_history(user_id, {"role": "system", "content": answer})
    return answer

def generate_final_plan_from_chat(user_id: int) -> Dict:
    history = redis_client.get_dialog_state(user_id)
    answer = exchange(system_prompt_analyze + history, "")
    redis_client.add_message_to_history(user_id, {"role": "system", "content": answer})
    answer = exchange(system_prompt_plan, answer)

def vectorize_all_users_in_redis():
    print("Векторизация пользователей (пока не реализована)...")
    pass

def find_similar_users(prompt: str, top_k: int = 5):
    print(f"Поиск похожих пользователей для промпта: '{prompt}' (пока не реализован)...")
    return [
        {"user_id": 1, "score": 0.99},
        {"user_id": 2, "score": 0.85},
    ]

