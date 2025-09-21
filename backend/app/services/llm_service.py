import json
import numpy as np
from typing import Dict, List
from ..core.redis_client import redis_client
from ..core.config import SCIBOX_API_KEY
from openai import OpenAI
from datetime import datetime, timezone

API_KEY = SCIBOX_API_KEY
BASE_URL = "https://llm.t1v.scibox.tech/v1"

system_prompt_info = "Ты — дружелюбный и эмпатичный карьерный консультант 'Навигатор'. Говорить, кто ты – НЕ НУЖНО. Приветствовать человека 'Привет' или 'Здравствуйте' – НЕ НУЖНО. Сразу переходи к делу. Твоя цель — узнать его 1) ФИО 2) отдел, должность и стаж работы 3) навыки (hard и soft skills) 4) последние 2 реализованных проекта 5) амбиции (вакансия, на которую хочет попасть пользователь). Вся уже собранная информация будет прикреплена последним абзацем в виде словаря (тебя будут интересовать элементы с ключом 'role' = 'user', 5 пунктов: ФИО, отдел/должность/стаж, навыки, проекты и амбиции). Информацию о пользователе ты ищешь по принципу первого вхождения: если, например, пользователь уже указал свое имя, ответив на твой вопрос, а затем снова написал какое-то другое, то ты не обращаешь внимания и обращаешься по первому имени. И так со всеми пунктами. Если ты видишь, что не все 5 пунктов закрыты полностью – задаешь пользователю уточняющие вопросы до тех пор, пока не соберется полная база знаний (в случае ФИО, например, нужно всегда просить абсолютно полное ФИО). Не переспрашивай ту информацию, что ты уже знаешь. Как только ты понимаешь, что база знаний полна информации по всем 5 пунктам – выведи её в чат с пометкой 'Вот вся текущая информация о Вас' и переспроси, не нужно ли что-то изменить/добавить. Если надо, то изменяешь/добавляешь и снова переспрашиваешь. Как только ты поймешь, что пользователь не хочет более ничего добавлять/изменять, скажи ему, что вся актуальная информация о нем записана, а по нажатию кнопки 'Сгенерировать и сохранить план' она обновит профиль и будет начат поиск оптимального карьерного плана. Будь вежливым, но не жеманным и льстительным. При необходимости обращайся по имени (если ты его уже знаешь). Вот текущая история общения с пользователем, где ты можешь найти информацию о нем:\n"

system_prompt_analyze = "Ты — дружелюбный и эмпатичный карьерный консультант 'Навигатор'. Говорить, кто ты – НЕ НУЖНО. Приветствовать человека 'Привет' или 'Здравствуйте' – НЕ НУЖНО. Сразу переходи к делу. Твоя цель — проанализировать уже собранные данные о пользователе и объяснить с учетом анализа, почему указанная в данном промпте (чуть ниже) вакансия/карьерный путь подходят ему больше всего, после чего вычленить всю информацию о требуемых навыках, обосновании их актуальности, конкретных шагах для получения вакансии и их описания (все эти данные бери только из того, что будет дальше в этом промпте, сам ничего не придумывай и никак не перефразируй – просто копируй уже прописанные навыки, шаги и их описания, слово в слово). Вся уже собранная информация о пользователе будет прикреплена предпоследним абзацем в виде словаря. Будь вежливым, но не жеманным и льстительным. При необходимости обращайся по имени. Вот информация о пользователе (если каких-то данных о пользователе нет – заполни соответсвующие поля в json 'нет данных'):\n"

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

def exchange(messages: list, temperature: float = 1, max_tokens: int = 10000, response_format = None):
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
    
def get_embedding(text: str) -> list[float]:
    try:
      client = OpenAI(api_key = API_KEY, base_url = BASE_URL)
      response = client.embeddings.create(
          model = "bge-m3",
          input = text
      )
      return response.data[0].embedding
    except Exception as e:
      return f"\n--- ПРОИЗОШЛА ОШИБКА ---\n{e}"

def cosine_similarity(vec1, vec2) -> float:
    v1, v2 = np.array(vec1), np.array(vec2)
    return abs(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

def euclidean_similarity(vec1, vec2) -> float:
    v1, v2 = np.array(vec1), np.array(vec2)
    return float(1 / (1 + np.linalg.norm(v1 - v2)))

def manhattan_similarity(vec1, vec2) -> float:
    v1, v2 = np.array(vec1), np.array(vec2)
    return float(1 / (1 + np.sum(np.abs(v1 - v2))))

def vectorize_all_users_in_redis():
    users = redis_client.get_all_users_info()
    for user in users:
        user_info = f"{user.get('position', '')} {user.get('about', '')} {' '.join(user.get('skills', []))}"
        redis_client.save_user_embedding(user.get('id'), get_embedding(user_info))

def find_best_career_plan(career_plans: List[Dict], career_plans_vec: List[List[float]], user_profile: Dict) -> Dict:
    vectorize_all_users_in_redis()
    user_vec = redis_client.get_user_embedding(user_profile.get('id'))
    best_match, best_score = None, -1
    for plan, plan_vec in zip(career_plans, career_plans_vec):
        score = cosine_similarity(user_vec, plan_vec)
        if score > best_score:
            best_match, best_score = plan, score
    return best_match
    
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

def find_courses(vacancy: str, courses: Dict[str, dict]) -> Dict[str, str]:
    matching_courses = {}
    for course_name, course_info in courses.items():
        if vacancy.lower() in map(str.lower, course_info.get("подходящие_вакансии", [])):
            matching_courses[course_name] = course_info.get("описание", "")
    return matching_courses

def generate_final_plan_from_chat(user_id: int) -> Dict:
    with open("backend/app/services/career_plans.json", "r") as f: career_plans = json.load(f)
    with open("backend/app/services/career_plans_vec.json", "r") as f: career_plans_vec = json.load(f)
    with open("backend/app/services/courses.json", "r") as f: courses = json.load(f)
    user_profile = redis_client.get_user_profile(user_id)
    best_plan = find_best_career_plan(career_plans, career_plans_vec, user_profile)
    best_courses = find_courses(best_plan.get("target_role", ""), courses)
    final_system_prompt = (
        f"{system_prompt_analyze}{user_profile}\n"
        f"Вот наиболее подходящий карьерный план для этого пользователя:\n{json.dumps(best_plan, ensure_ascii = False)}"
        "После анализа, твоя задача — вернуть результат ИСКЛЮЧИТЕЛЬНО в формате JSON, "
        "без каких-либо вводных слов или комментариев. "
        f"Структура JSON должна строго соответствовать этому примеру: {json.dumps(example_plan, ensure_ascii = False)}\n\n"
    )
    messages_for_llm = [{"role": "system", "content": final_system_prompt}]
    answer = exchange(
        messages_for_llm,
        temperature = 1,
        max_tokens = 5000,
        response_format = {"type": "json_object"}
    )
    plan_data = json.loads(answer)
    plan_data['plan_id'] = f"plan_{int(datetime.now().timestamp())}_user_{user_id}"
    plan_data['created_at'] = datetime.now(timezone.utc).isoformat()
    plan_data['relevant_courses'] = best_courses
    redis_client.clear_active_chat_history(user_id)
    return plan_data

def extract_profile_data_from_chat(history: List[Dict]) -> Dict:
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
    return json.loads(exchange(messages_for_llm, response_format = {"type": "json_object"}))

def lemmatization(hr_text: str) -> Dict:
    system_prompt = """
    Вы специалист по морфологическому анализу текста. 
    Ваша задача — выполнять лемматизацию русских и английских слов, приводя их к начальной словарной форме с учетом контекста и части речи.
    \n\nИНСТРУКЦИИ ПО ЛЕММАТИЗАЦИИ:\n
    1. Анализируйте контекст каждого слова для определения правильной части речи\n
    2. Учитывайте морфологические особенности языка (падежи, времена, числа, лица)\n
    3. Для омонимов используйте контекст для выбора правильной леммы\n
    4. Сохраняйте пунктуацию и специальные символы без изменений\n
    5. Обрабатывайте неологизмы и редкие слова на основе морфологических правил\n\n
    Итоговый ответ упакуй в JSOM с единственным ключом "lemmas", значением которого будет список лемматизированных слов.
    ФОРМАТ ОТВЕТА: Отвечайте ТОЛЬКО валидным JSON без дополнительного текста. """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": hr_text}
    ]
    raw_response = exchange(messages, response_format = {"type": "json_object"})
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        return {"error": "Не удалось распарсить ответ модели", "raw_response": raw_response}

def find_similar_users(hr_text: str, top_k: int = 5) -> List[Dict]:
    hr_request = lemmatization(hr_text)
    hr_vec = get_embedding(" ".join(hr_request.get("lemmas", [])))
    vectorize_all_users_in_redis()
    users = redis_client.get_all_users_info()
    scored_users = []
    for user in users:
        if user.get("id") == '1' or user.get("profile", {}).get("role") == 'HR' or (not user.get("about", [])): continue
        user_vec = redis_client.get_user_embedding(user.get("id"))
        if user_vec is None: continue
        similarity = cosine_similarity(hr_vec, user_vec)
        scored_users.append({
            "user_id": user.get("id"),
            "score": similarity
        })
    return scored_users[:top_k]