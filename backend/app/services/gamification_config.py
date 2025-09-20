# --- События и XP ---
GAME_EVENTS = {
    "PROFILE_UPDATED": {"xp": 0}, 
    "FIRST_CHAT_MESSAGE": {"xp": 10},
    "CAREER_PLAN_GENERATED": {"xp_first": 200, "xp_subsequent": 50},
    "NIGHT_OWL_ACTION": {"xp": 25},
}

# --- Достижения ---
ACHIEVEMENTS = {
    "ACH_PROFILE_100": {"name": "Архитектор своей судьбы", "description": "Ваш профиль полностью заполнен!", "icon": "ach_profile_100.png"},
    "ACH_FIRST_PLAN": {"name": "Первый шаг сделан", "description": "Вы сгенерировали свой первый карьерный план.", "icon": "ach_first_plan.png"},
    "ACH_STRATEGIST": {"name": "Стратегический мыслитель", "description": "Вы сгенерировали 3 карьерных плана.", "icon": "ach_strategist.png"},
    "ACH_SKILL_MASTER": {"name": "Мастер на все руки", "description": "В вашем профиле более 10 навыков.", "icon": "ach_skill_master.png"},
    "ACH_NIGHT_OWL": {"name": "Ночная сова", "description": "Работа кипит даже ночью!", "icon": "ach_night_owl.png"},
}

ACHIEVEMENT_CONDITIONS = {
    "ACH_PROFILE_100": {"type": "profile_check"},
    "ACH_FIRST_PLAN": {"type": "plan_count", "count": 1},
    "ACH_STRATEGIST": {"type": "plan_count", "count": 3},
    "ACH_SKILL_MASTER": {"type": "skill_count", "count": 10},
    "ACH_NIGHT_OWL": {"type": "time_check", "start_hour": 2, "end_hour": 4} # UTC
}

# --- Формула уровня ---
def calculate_level(xp: int) -> int:
    return int((xp / 100)**0.5) + 1