import json
from typing import Dict, List
from app.core.redis_client import redis_client
from openai import OpenAI
from datetime import datetime, timezone

API_KEY = "sk-LqCf11ej9dj70ObUG956eQ"
BASE_URL = "https://llm.t1v.scibox.tech/v1"

system_prompt_info = "Ты — дружелюбный и эмпатичный карьерный консультант 'Навигатор'. Говорить, кто ты – НЕ НУЖНО. Приветствовать человека 'Привет' или 'Здравствуйте' – НЕ НУЖНО. Сразу переходи к делу. Твоя цель — узнать его 1) ФИО 2) отдел, должность и стаж работы 3) навыки (hard и soft skills) 4) последние 2 реализованных проекта 5) амбиции (вакансия, на которую хочет попасть пользователь). Вся уже собранная информация будет прикреплена последним абзацем в виде словаря (тебя будут интересовать элементы с ключом 'role' = 'user', 5 пунктов: ФИО, отдел/должность/стаж, навыки, проекты и амбиции). Информацию о пользователе ты ищешь по принципу первого вхождения: если, например, пользователь уже указал свое имя, ответив на твой вопрос, а затем снова написал какое-то другое, то ты не обращаешь внимания и обращаешься по первому имени. И так со всеми пунктами. Если ты видишь, что не все 5 пунктов закрыты полностью – задаешь пользователю уточняющие вопросы до тех пор, пока не соберется полная база знаний (в случае ФИО, например, нужно всегда просить абсолютно полное ФИО). Не переспрашивай ту информацию, что ты уже знаешь. Как только ты понимаешь, что база знаний полна информации по всем 5 пунктам – предложи ему заполнить профиль автоматически. Будь вежливым, но не жеманным и льстительным. При необходимости обращайся по имени (если ты его уже знаешь). Вот текущая история общения с пользователем, где ты можешь найти информацию о нем:\n"

system_prompt_analyze = "Ты — дружелюбный и эмпатичный карьерный консультант 'Навигатор'. Говорить, кто ты – НЕ НУЖНО. Приветствовать человека 'Привет' или 'Здравствуйте' – НЕ НУЖНО. Сразу переходи к делу. Твоя цель — построить последовательный карьерный план на основании известной о пользователе информации. Вся уже собранная информация будет прикреплена последним абзацем в виде словаря (тебя будут интересовать элементы с ключом 'role' = 'user', 5 пунктов: ФИО, отдел/должность/стаж, навыки, проекты и амбиции). Информацию о пользователе ты ищешь по принципу первого вхождения: если, например, пользователь уже указал свое имя, ответив на твой вопрос, а затем снова написал какое-то другое, то ты не обращаешь внимания и обращаешься по первому имени. И так со всеми пунктами. Будь вежливым, но не жеманным и льстительным. При необходимости обращайся по имени. Вот текущая история общения с пользователем, где ты можешь найти информацию о нем:\n"


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

def exchange(messages: list, temperature: float = 1, max_tokens: int = 2000, response_format = None):
    try:
        client = OpenAI(api_key = API_KEY, base_url = BASE_URL)
        resp = client.chat.completions.create(
            model = "Qwen2.5-72B-Instruct-AWQ",
            messages = messages,
            response_format = response_format,
            temperature = temperature,
            max_tokens = max_tokens,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"\n--- ПРОИЗОШЛА ОШИБКА ---\n{e}"
    
def get_next_chat_response(user_id: int, user_prompt: str) -> str:
    history = redis_client.get_active_chat_history(user_id)
    history.append({"role": "user", "content": user_prompt})
    profile_info = ""
    if len(history) == 1: 
        profile = redis_client.get_user_profile(user_id)
        skills = redis_client.get_user_skills(user_id)
        if profile and profile.get('about') and skills:
            profile_summary = (
                f"Имя: {profile.get('name', 'неизвестно')}, "
                f"Должность: {profile.get('position', 'неизвестна')}, "
                f"Навыки: {', '.join(skills)}"
            )
            profile_info = (
                f"\n\nВАЖНАЯ ИНФОРМАЦИЯ: У этого пользователя уже заполнен профиль. Вот краткая сводка: {profile_summary}. "
                "Твоя задача — вежливо подтвердить, что ты видишь эти данные, и предложить построить карьерный план на их основе. "
                "Обязательно спроси, не хочет ли пользователь что-то уточнить или изменить в своих данных перед началом анализа."
            )
        else:
            profile_info = (
                "\n\nВАЖНАЯ ИНФОРМАЦИЯ: Профиль этого пользователя пуст. "
                "Твоя первоочередная задача — начать диалог для сбора информации по 5 ключевым пунктам, чтобы в конце предложить ему автоматически заполнить профиль."
            )

    contextual_system_prompt = system_prompt_info + profile_info
    
    messages_for_llm = [{"role": "system", "content": contextual_system_prompt}] + history
    redis_client.add_message_to_active_history(user_id, {"role": "user", "content": user_prompt})
    answer = exchange(messages_for_llm)
    redis_client.add_message_to_active_history(user_id, {"role": "assistant", "content": answer})
    return answer


def generate_final_plan_from_chat(user_id: int) -> Dict:
    history = redis_client.get_active_chat_history(user_id)
    final_system_prompt = (
        f"{system_prompt_analyze}\n\n"
        "После анализа, твоя задача — вернуть результат ИСКЛЮЧИТЕЛЬНО в формате JSON, без каких-либо вводных слов или комментариев. "
        f"Структура JSON должна строго соответствовать этому примеру: {json.dumps(example_plan, ensure_ascii=False)}"
    )
    messages_for_llm = [{"role": "system", "content": final_system_prompt}] + history
    answer = exchange(messages_for_llm, response_format={"type": "json_object"})
    plan_data = json.loads(answer)
    plan_data['plan_id'] = f"plan_{int(datetime.now().timestamp())}_user_{user_id}"
    plan_data['created_at'] = datetime.now(timezone.utc).isoformat()
    redis_client.clear_active_chat_history(user_id)
    return plan_data

def vectorize_all_users_in_redis():
    print("Векторизация пользователей (пока не реализована)...")
    pass

def find_similar_users(prompt: str, top_k: int = 5):
    print(f"Поиск похожих пользователей для промпта: '{prompt}' (пока не реализован)...")
    return [
        {"user_id": 1, "score": 0.99},
        {"user_id": 2, "score": 0.85},
    ]

def extract_profile_data_from_chat(history: List[Dict]) -> Dict:
    """
    Извлекает структурированные данные (ФИО, навыки и т.д.) из диалога.
    """
    extraction_prompt = (
        "Проанализируй предоставленный диалог между пользователем и карьерным консультантом. "
        "Твоя задача — извлечь из ответов пользователя следующую информацию и вернуть ее в формате JSON: "
        "`name` (string, полное ФИО), `position` (string, текущая должность), "
        "`about` (string, краткое саммари о пользователе на основе его ответов), "
        "`skills` (list of strings, список ключевых навыков). "
        "Если какую-то информацию найти не удалось, оставь соответствующее поле пустым. "
        "Верни только JSON объект, без лишних слов."
    )
    
    messages_for_llm = history + [{"role": "system", "content": extraction_prompt}]

    return json.loads(exchange(messages_for_llm, response_format={"type": "json_object"}))