from datetime import datetime, timezone
from ..core.redis_client import redis_client
from .gamification_config import GAME_EVENTS, ACHIEVEMENTS, ACHIEVEMENT_CONDITIONS, calculate_level

class GamificationService:
    def process_event(self, user_id: int, event_key: str, event_data: dict = None):
        if event_data is None: event_data = {}

        current_stats = redis_client.get_gamification_stats(user_id)
        current_achievements = redis_client.get_user_achievements(user_id)
        
        xp_added = 0
        unlocked_achievements = []

        if event_key == "PROFILE_UPDATED":
            old_profile = event_data.get("old_profile", {})
            new_profile = event_data.get("new_profile", {})
            if not redis_client.get_user_gamification_flag(user_id, "about_filled") and new_profile.get('about'):
                xp_added += 50; redis_client.set_user_gamification_flag(user_id, "about_filled", "true")
            if not redis_client.get_user_gamification_flag(user_id, "name_filled") and new_profile.get('name'):
                xp_added += 20; redis_client.set_user_gamification_flag(user_id, "name_filled", "true")
            if not redis_client.get_user_gamification_flag(user_id, "photo_filled") and new_profile.get('photo_url'):
                xp_added += 30; redis_client.set_user_gamification_flag(user_id, "photo_filled", "true")

            old_skills = set(old_profile.get('skills', []))
            new_skills = set(new_profile.get('skills', []))
            added_skills_count = len(new_skills - old_skills)
            if added_skills_count > 0:
                xp_added += added_skills_count * 10

        elif event_key == "CAREER_PLAN_GENERATED":
            plans_count = len(redis_client.get_all_career_plans(user_id))
            if plans_count == 1:
                xp_added = GAME_EVENTS[event_key]['xp_first']
            else:
                xp_added = GAME_EVENTS[event_key]['xp_subsequent']

        elif event_key == "FIRST_CHAT_MESSAGE" and "ACH_FIRST_STEP" not in current_achievements:
             xp_added = GAME_EVENTS[event_key]['xp']

        now_hour = datetime.now(timezone.utc).hour
        if 2 <= now_hour < 4:
            last_bonus_date = redis_client.get_user_gamification_flag(user_id, "last_night_owl_bonus")
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if last_bonus_date != today_str:
                xp_added += GAME_EVENTS["NIGHT_OWL_ACTION"]['xp']
                redis_client.set_user_gamification_flag(user_id, "last_night_owl_bonus", today_str)

        current_stats['xp'] += xp_added
        new_level = calculate_level(current_stats['xp'])
        level_up = new_level > current_stats.get('level', 1)
        current_stats['level'] = new_level

        profile = redis_client.get_user_profile(user_id)
        skills = redis_client.get_user_skills(user_id)
        plans = redis_client.get_all_career_plans(user_id)

        new_profile_data = event_data.get("new_profile", {})
        new_skills = set(new_profile_data.get('skills', []))

        for ach_key, condition in ACHIEVEMENT_CONDITIONS.items():
            if ach_key not in current_achievements:
                unlocked = False
                if condition['type'] == 'event' and condition['event'] == event_key:
                    unlocked = True
                elif condition['type'] == 'plan_count' and len(plans) >= condition['count']:
                    unlocked = True
                elif condition['type'] == 'skill_count' and len(new_skills) >= condition['count']:
                    unlocked = True
                elif condition['type'] == 'profile_check':
                    if new_profile_data.get('name') and new_profile_data.get('about') and new_profile_data.get('photo_url') and new_skills:
                        unlocked = True
                
                if unlocked:
                    unlocked_achievements.append(ACHIEVEMENTS[ach_key])
                    redis_client.add_achievement(user_id, ach_key)

        redis_client.update_xp_and_level(user_id, current_stats['xp'], current_stats['level'])
        
        return {
            "xp_added": xp_added, "total_xp": current_stats['xp'],
            "level": new_level, "level_up": level_up,
            "unlocked_achievements": unlocked_achievements
        }

gamification_service = GamificationService()