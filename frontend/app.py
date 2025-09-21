import os
import streamlit as st
import api_client
import time
from typing import Dict

# --- Конфигурация страницы ---
st.set_page_config(
    layout="wide",
    page_title="Talent Navigator AI",
    page_icon="🚀"
)

HIDE_DEFAULT_FORMAT = """
<style>
header [data-testid="stToolbar"] {visibility: hidden !important;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

st.markdown(HIDE_DEFAULT_FORMAT, unsafe_allow_html=True)
# --- Инициализация состояния сессии ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = {}

# =====================================================================================
# --- СТРАНИЦА ВХОДА ---
# =====================================================================================
def show_login_page():
    """Отрисовывает интерфейс для входа в систему."""
    with st.container():
        st.title("Добро пожаловать в Talent Navigator AI!")
        st.caption("Ваш умный помощник в карьерном развитии и поиске талантов.")
        
        with st.form("login_form"):
            username = st.text_input("Имя пользователя")
            password = st.text_input("Пароль", type="password")
            
            submitted = st.form_submit_button("Войти", use_container_width=True, type="primary")

            if submitted:
                with st.spinner("Аутентификация..."):
                    user_data = api_client.login(username, password)
                    if user_data and user_data.get("success"):
                        st.session_state.logged_in = True
                        st.session_state.user_info = user_data
                        st.rerun()

# =====================================================================================
# --- СТРАНИЦА РАБОТНИКА ---
# =====================================================================================

def show_employee_page():
    st.title(f"👋 Привет, {st.session_state.user_info.get('name')}!")
    st.caption("Это ваш личный карьерный навигатор. Здесь вы можете отслеживать свой прогресс, строить планы развития и получать предложения о новых ролях.")

    if "event_response" in st.session_state and st.session_state.event_response:
        response = st.session_state.event_response
        if response.get("unlocked_achievements"):
            for ach in response["unlocked_achievements"]:
                st.toast(f"🏆 Новое достижение: {ach['name']}!", icon="🏆")
                st.balloons()

        if response.get("xp_added", 0) > 0:
            st.toast(f"✨ +{response['xp_added']} XP!")

        st.session_state.event_response = None
        st.cache_data.clear() 

    st.markdown("---")

    tab_profile, tab_plan, tab_offers = st.tabs([
        "👤 Мой профиль", 
        "🗺️ Карьерный план", 
        "📬 Офферы"
    ])

    user_id = st.session_state.user_info.get('user_id')

    # =====================================================================================
    # --- ВКЛАДКА 1: МОЙ ПРОФИЛЬ ---
    # =====================================================================================
    with tab_profile:
        @st.cache_data(ttl=10) 
        def get_all_profile_data(uid):
            profile = api_client.get_user_profile(uid)
            gamification = api_client.get_user_progress(uid)
            achievements = api_client.get_user_achievements_status(uid)
            return profile, gamification, achievements
        
        profile_data, gamification_data, achievements_data = get_all_profile_data(user_id)
        
        if "edit_mode" not in st.session_state: st.session_state.edit_mode = False
        
        if not st.session_state.edit_mode:
            if st.button("✏️ Редактировать профиль"):
                st.session_state.edit_mode = True
                st.rerun()

        if st.session_state.edit_mode:
            with st.container(border=True):
                st.subheader("Редактирование профиля")
                with st.form("edit_profile_form"):
                    name_val = profile_data.get("name", "")
                    nickname_val = profile_data.get("nickname", "")
                    photo_url_val = profile_data.get("photo_url", "")
                    about_val = profile_data.get("about", "")
                    skills_list = profile_data.get("skills", [])
                    skills_val = ", ".join(skills_list)
                    new_name = st.text_input("Ваше ФИО", value=name_val)
                    new_nickname = st.text_input("Никнейм (логин)", value=nickname_val)
                    new_photo_url = st.text_input("URL аватара", value=photo_url_val)
                    new_about = st.text_area("Обо мне", value=about_val, height=150)
                    new_skills_str = st.text_input("Навыки (через запятую)", value=skills_val)
                    
                    col1, col2 = st.columns([1,1])
                    with col1:
                        if st.form_submit_button("Сохранить", use_container_width=True, type="primary"):
                            new_skills_list = [skill.strip() for skill in new_skills_str.split(",") if skill.strip()]
                            old_profile_for_event = {"skills": profile_data.get('skills', [])}
                            new_profile_for_event = {"about": new_about, "skills": new_skills_list, "name": new_name, "photo_url": new_photo_url}
                            
                            with st.spinner("Сохранение..."):
                                api_client.update_user_profile(user_id, name=new_name, nickname=new_nickname, about=new_about, photo_url=new_photo_url, skills=new_skills_list)
                                st.session_state.event_response = api_client.trigger_gamification_event(user_id, "PROFILE_UPDATED", {"old_profile": old_profile_for_event, "new_profile": new_profile_for_event})
                            
                            st.session_state.edit_mode = False
                            st.rerun()
                    with col2:
                        if st.form_submit_button("Отмена", use_container_width=True):
                            st.session_state.edit_mode = False
                            st.rerun()

        if not profile_data or not gamification_data or not achievements_data:
            st.error("Не удалось загрузить данные профиля.")
        else:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(profile_data.get("photo_url", ""), use_container_width=True, caption=profile_data.get("nickname"))
            with col2:
                st.header(profile_data.get("name"))
                st.subheader(profile_data.get("position", "Должность не указана"))
                st.markdown(f"**Обо мне:** {profile_data.get('about') or 'Информация не заполнена.'}")
            st.markdown("---")
            st.subheader("Ключевые навыки")
            skills = profile_data.get("skills", [])
            if skills:
                st.info(" ".join([f"`{skill.upper()}`" for skill in skills]))
            else:
                st.warning("Вы еще не добавили ни одного навыка.")
            st.markdown("---")
            st.subheader("Ваш прогресс")
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                st.metric("✨ Очки опыта (XP)", gamification_data.get('xp', 0))
            with g_col2:
                st.metric("🚀 Уровень", f"Lvl {gamification_data.get('level', 1)}")

            level = gamification_data.get('level', 1)
            xp = gamification_data.get('xp', 0)
            xp_current_level = ((level - 1)**2) * 100
            xp_for_next_level = (level**2) * 100
            xp_needed = xp_for_next_level - xp_current_level
            xp_progress_in_level = xp - xp_current_level
            progress_percent = xp_progress_in_level / xp_needed if xp_needed > 0 else 1.0
            st.progress(progress_percent, text=f"{xp_progress_in_level} / {xp_needed} XP до следующего уровня")

            st.markdown("##### Ваши награды")
            all_ach = achievements_data.get('achievements', [])
            if all_ach:
                num_columns = len(all_ach)
                cols = st.columns(num_columns)
                for i, ach in enumerate(all_ach):
                    with cols[i % num_columns]:
                        icon_url = f"http://localhost:8000/assets/icons/{ach['icon']}"
                        if not ach['unlocked']:
                            icon_url += "?grayscale=true"
                        st.image(icon_url, width=80, caption=f"**{ach['name']}**" if ach['unlocked'] else ach['name'])
            
            with st.expander("⚙️ Настройки профиля"):
                st.toggle("Скрыть карьерный путь", value=True)
                if st.button("Сохранить настройки", type="secondary"): 
                    st.toast("Настройки сохранены (симуляция)")

    # =====================================================================================
    # --- ВКЛАДКА 2: КАРЬЕРНЫЙ ПЛАН ---
    # =====================================================================================
        with tab_plan:
            st.header("🗺️ Ваши карьерные планы")
            user_id = st.session_state.user_info.get('user_id')

            if 'chat_active' not in st.session_state: st.session_state.chat_active = False
            if 'processing_bot_response' not in st.session_state: st.session_state.processing_bot_response = False
            if "messages" not in st.session_state: st.session_state.messages = []
            if 'generated_plan' not in st.session_state: st.session_state.generated_plan = None

            if not st.session_state.generated_plan:
                with st.spinner("Загрузка сохраненных планов..."):
                    saved_plans_data = api_client.get_all_career_plans(user_id)
                if saved_plans_data and saved_plans_data.get("plans"):
                    st.subheader("Сохраненные планы")
                    plans = saved_plans_data["plans"]
                    for i, plan in enumerate(reversed(plans)):
                        title = plan.get('plan_title', f'План {len(plans)-i}')
                        date = plan.get('created_at', 'Неизвестная дата')[:10]
                        with st.expander(f"**{title}** (от {date})"):
                            st.success(f"**Анализ:** {plan.get('current_analysis', 'Нет данных.')}")
                            path = plan.get('recommended_path', {})
                            st.info(f"**Рекомендация:** {path.get('target_role', 'Не определена')}. **Обоснование:** {path.get('why_it_fits', 'Нет данных.')}")
                            st.markdown("**Навыки для развития:**")
                            skill_gap = plan.get("skill_gap", [])
                            if skill_gap:
                                for gap in skill_gap: st.markdown(f"- **`{gap.get('skill')}`** — {gap.get('reason')}")
                            st.markdown("**План действий:**")
                            action_steps = plan.get("actionable_steps", [])
                            if action_steps:
                                for step in action_steps: st.markdown(f"**{step.get('step')}. ({step.get('type')}):** {step.get('description')} ({step.get('timeline')})")
                else:
                    st.info("У вас пока нет сохраненных планов. Создайте свой первый план с помощью ИИ-консультанта!")
                st.markdown("---")

            if not st.session_state.chat_active and not st.session_state.generated_plan:
                if st.button("💬 Начать новый диалог...", use_container_width=True, type="primary"):
                    api_client.clear_chat_history(user_id)
                    st.session_state.event_response = api_client.trigger_gamification_event(user_id, "FIRST_CHAT_MESSAGE")
                    st.session_state.chat_active = True
                    st.rerun()

            elif st.session_state.chat_active:
                st.subheader("Создание нового плана")
                chat_container = st.container(height=400, border=True)
                if not st.session_state.get("messages"):
                    with st.spinner("Загрузка диалога..."):
                        history_data = api_client.get_chat_history(user_id)
                    if history_data and history_data.get("history"):
                        st.session_state.messages = history_data["history"]
                    else:
                        st.session_state.messages = [{"role": "assistant", "content": "Привет! Я 'Навигатор'. Давайте начнем. Расскажите немного о себе, и мы вместе построим ваш новый карьерный план."}]
                
                for message in st.session_state.messages:
                    with chat_container.chat_message(message["role"]): st.markdown(message["content"])
                
                if st.session_state.processing_bot_response:
                    with chat_container.chat_message("assistant"):
                        placeholder = st.empty()
                        placeholder.markdown("Печатаю...")
                        last_user_message = next((msg["content"] for msg in reversed(st.session_state.messages) if msg["role"] == "user"), None)
                        if last_user_message:
                            response_data = api_client.get_chat_response(user_id, last_user_message)
                            bot_response = response_data.get("response", "Извините, произошла ошибка.") if response_data else "Не удалось получить ответ от сервера."
                            placeholder.markdown(bot_response)
                            st.session_state.messages.append({"role": "assistant", "content": bot_response})
                            st.session_state.processing_bot_response = False
                            st.rerun()
                
                if prompt := st.chat_input("Напишите ваше сообщение..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.processing_bot_response = True
                    st.rerun()

                col1, col2 = st.columns([3, 1])
                with col1:
                    if len(st.session_state.messages) > 3:
                        if st.button("✅ Сгенерировать и сохранить план", use_container_width=True):
                            with st.spinner("Систематизирую всю информацию..."):
                                plan_data_response = api_client.generate_final_plan_from_chat(user_id)
                                if plan_data_response and plan_data_response.get("plan"):
                                    api_client.save_career_plan(user_id, plan_data_response.get("plan"))
                                    st.session_state.event_response = api_client.trigger_gamification_event(user_id, "CAREER_PLAN_GENERATED")
                                    st.session_state.generated_plan = plan_data_response.get("plan")
                                    st.session_state.chat_active = False
                                    st.cache_data.clear()
                                    st.rerun()
                with col2:
                    if st.button("❌ Отменить", use_container_width=True):
                        with st.spinner("Отмена диалога..."):
                            api_client.clear_chat_history(user_id)
                        st.session_state.chat_active = False
                        st.session_state.messages = []
                        st.rerun()

            if st.session_state.generated_plan:
                st.success("План успешно создан и сохранен!")
                st.balloons()
                plan = st.session_state.generated_plan
                st.subheader(plan.get('plan_title', 'Ваш новый карьерный план'))
                st.success(f"**Анализ:** {plan.get('current_analysis', 'Нет данных.')}")
                path = plan.get('recommended_path', {})
                st.info(f"**Рекомендация:** {path.get('target_role', 'Не определена')}. **Обоснование:** {path.get('why_it_fits', 'Нет данных.')}")
                st.markdown("**Навыки для развития:**")
                skill_gap = plan.get("skill_gap", [])
                if skill_gap:
                    for gap in skill_gap: st.markdown(f"- **`{gap.get('skill')}`** — {gap.get('reason')}")
                st.markdown("**План действий:**")
                action_steps = plan.get("actionable_steps", [])
                if action_steps:
                    for step in action_steps: st.markdown(f"**{step.get('step')}. ({step.get('type')}):** {step.get('description')} ({step.get('timeline')})")
                if st.button("Отлично, спасибо!"):
                    st.session_state.chat_active = False
                    st.session_state.generated_plan = None
                    st.cache_data.clear()
                    st.rerun()

    # =====================================================================================
    # --- ВКЛАДКА 3: ОФФЕРЫ ---
    # =====================================================================================
    with tab_offers:
        st.header("📬 Ваши предложения")
        user_id = st.session_state.user_info.get('user_id')
        offers = api_client.get_user_offers(user_id)
        if offers is None:
            st.error("Не удалось загрузить офферы.")
        elif not offers:
            st.success("У вас пока нет новых предложений.")
        else:
            for offer in offers:
                with st.container(border=True):
                    hr_profile = api_client.get_user_profile(offer['from_hr_id'])
                    hr_name = hr_profile.get('name') if hr_profile else "Неизвестный HR"
                    st.subheader(offer['title'])
                    st.caption(f"От: {hr_name}")
                    st.info(f"Статус: {offer['status']}")
                    with st.expander("Показать описание"):
                        st.write(offer['description'])
                    if offer['status'] == "Отправлено":
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("👍 Принять", key=f"accept_{offer['id']}", use_container_width=True):
                                api_client.update_offer_status(offer['id'], "Принято")
                                st.toast("Оффер принят!")
                                st.rerun()
                        with c2:
                            if st.button("👎 Отклонить", key=f"decline_{offer['id']}", use_container_width=True):
                                api_client.update_offer_status(offer['id'], "Отклонено")
                                st.toast("Оффер отклонен.")
                                st.rerun()

# =====================================================================================
# --- СТРАНИЦА HR ---
# =====================================================================================
def show_hr_page():
    st.title(f"📇 Панель HR-специалиста, {st.session_state.user_info.get('name')}")
    st.caption("Используйте умный поиск для нахождения идеальных кандидатов на основе их опыта и навыков.")
    
    # --- Инициализация состояний ---
    if 'sending_offer_to' not in st.session_state: st.session_state.sending_offer_to = None
    if 'search_results' not in st.session_state: st.session_state.search_results = None
    if 'viewing_profile_id' not in st.session_state: st.session_state.viewing_profile_id = None

    if st.session_state.viewing_profile_id:
        @st.dialog("Профиль кандидата", width="large")
        def show_profile_dialog():
            profile_id = st.session_state.viewing_profile_id
            
            @st.cache_data(ttl=10) 
            def get_all_profile_data(uid):
                profile = api_client.get_user_profile(uid)
                gamification = api_client.get_user_progress(uid)
                achievements = api_client.get_user_achievements_status(uid)
                return profile, gamification, achievements
            
            profile_data, gamification_data, achievements_data = get_all_profile_data(profile_id)
            
            if not profile_data:
                st.error("Не удалось загрузить профиль этого пользователя.")
            else:
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(profile_data.get("photo_url", ""), use_column_width=True, caption=profile_data.get("nickname"))
                with col2:
                    st.header(profile_data.get("name"))
                    st.subheader(profile_data.get("position", "Должность не указана"))
                    st.markdown(f"**Обо мне:** *{profile_data.get('about') or 'Информация не заполнена.'}*")
                
                st.markdown("---")
                st.subheader("Ключевые навыки")
                skills = profile_data.get("skills", [])
                if skills: st.info(" ".join([f"`{skill.upper()}`" for skill in skills]))
                else: st.warning("Пользователь не добавил ни одного навыка.")
                
                st.markdown("---")
                st.subheader("Прогресс и достижения")
                g_col1, g_g_col2 = st.columns(2)
                with g_col1:
                    st.metric("✨ Очки опыта (XP)", gamification_data.get('xp', 0))
                with g_g_col2:
                    st.metric("🚀 Уровень", f"Lvl {gamification_data.get('level', 1)}")
                all_ach = achievements_data.get('achievements', [])
                if all_ach:
                    cols = st.columns(len(all_ach))
                    for i, ach in enumerate(all_ach):
                        with cols[i]:
                            icon_url = f"http://localhost:8000/assets/icons/{ach['icon']}"
                            if not ach['unlocked']: icon_url += "?grayscale=true"
                            st.image(icon_url, width=64, caption=f"**{ach['name']}**" if ach['unlocked'] else ach['name'])
            
            if st.button("Закрыть", use_container_width=True):
                st.session_state.viewing_profile_id = None
                st.rerun()

        show_profile_dialog()

    st.markdown("---")
    tab_search, tab_my_offers = st.tabs(["🔍 Поиск кандидатов", "📄 Мои офферы"])

    with tab_search:
        st.header("🧠 Умный поиск кандидатов")
        
        if st.session_state.sending_offer_to:
            user_profile = api_client.get_user_profile(st.session_state.sending_offer_to)
            candidate_name = user_profile.get('name') if user_profile else "Неизвестный кандидат"
            with st.container(border=True):
                st.subheader(f"Отправка оффера для: {candidate_name}")
                with st.form("offer_form"):
                    title = st.text_input("Название вакансии / проекта")
                    description = st.text_area("Описание оффера", height=200, placeholder="Подробно опишите роль, задачи и условия...")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("✅ Отправить оффер", type="primary", use_container_width=True):
                            if title and description:
                                hr_id = st.session_state.user_info.get('user_id')
                                with st.spinner("Отправка..."):
                                    api_client.create_offer(from_hr_id=hr_id, to_user_id=st.session_state.sending_offer_to, title=title, description=description)
                                st.success(f"Оффер для {candidate_name} успешно отправлен!")
                                st.session_state.sending_offer_to = None
                                st.rerun()
                            else:
                                st.warning("Пожалуйста, заполните все поля.")
                    with c2:
                        if st.form_submit_button("❌ Отмена", use_container_width=True):
                            st.session_state.sending_offer_to = None
                            st.rerun()

        with st.form("search_form"):
            search_prompt = st.text_area("Описание идеального кандидата:", height=150, placeholder="Например: 'Ищу опытного разработчика на Python со знанием облачных технологий...'")
            submitted = st.form_submit_button("Найти кандидатов", type="primary", use_container_width=True)
            if submitted and search_prompt:
                with st.spinner("ИИ анализирует профили сотрудников..."):
                    st.session_state.search_results = api_client.match_candidates(search_prompt)
        
        st.markdown("---")
        st.subheader("🏆 Результаты поиска:")
        
        if st.session_state.search_results is not None:
            if not st.session_state.search_results:
                st.warning("Не найдено подходящих кандидатов по вашему запросу.")
            else:
                sorted_results = sorted(st.session_state.search_results, key=lambda x: x['score'], reverse=True)
                for result in sorted_results:
                    level = result.get('level', 1)
                    border_color = "#808080"
                    if level >= 5: border_color = "#DC143C"
                    elif level >= 4: border_color = "#2E8B57"
                    elif level >= 3: border_color = "#4169E1"
                    elif level >= 2: border_color = "#FFD700"
                    
                    st.markdown(f'<div style="border: 2px solid {border_color}; border-radius: 10px; padding: 15px; margin-bottom: 10px;">', unsafe_allow_html=True)
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.subheader(f"{result.get('name')} (Lvl {level})")
                        st.caption(f"Должность: {result.get('position')}")
                    with col2:
                        match_percent = int(result.get('score', 0) * 100)
                        st.progress(match_percent, text=f"Релевантность: {match_percent}%")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Посмотреть профиль", key=f"view_{result.get('user_id')}", use_container_width=True):
                            st.session_state.viewing_profile_id = result.get('user_id')
                            st.rerun()
                    with c2:
                        if st.button("✍️ Отправить оффер", key=f"offer_{result.get('user_id')}", use_container_width=True, type="secondary"):
                            st.session_state.sending_offer_to = result.get('user_id')
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Введите запрос и нажмите 'Найти кандидатов', чтобы увидеть результаты.")
    
    with tab_my_offers:
        st.header("📄 Отслеживание отправленных офферов")
        hr_id = st.session_state.user_info.get('user_id')
        sent_offers = api_client.get_hr_offers(hr_id)
        if sent_offers is None:
            st.error("Не удалось загрузить отправленные офферы.")
        elif not sent_offers:
            st.info("Вы еще не отправили ни одного оффера.")
        else:
            display_data = []
            for offer in sent_offers:
                user_profile = api_client.get_user_profile(offer['to_user_id'])
                user_name = user_profile.get('name') if user_profile else "Неизвестный сотрудник"
                display_data.append({ "candidate_name": user_name, "vacancy": offer['title'], "sent_at": offer.get('timestamp', '').strip('"'), "status": offer['status'] })
            st.data_editor(display_data, column_config={"candidate_name": "Кандидат", "vacancy": "Вакансия", "sent_at": "Отправлено", "status": "Статус"}, hide_index=True, use_container_width=True, disabled=True)
# =====================================================================================
# --- СТРАНИЦА АДМИНА ---
# =====================================================================================
def show_admin_page():
    st.title("🛠️ Панель администратора")
    with st.expander("Создать нового пользователя", expanded=False):
        with st.form("create_user_form", clear_on_submit=False): # clear_on_submit=False, чтобы показать пароль
            st.subheader("Данные нового пользователя")
            new_name = st.text_input("ФИО")
            new_username = st.text_input("Логин (username)")
            new_role = st.selectbox("Роль", ["Работник", "HR"], index=0)
            
            submitted = st.form_submit_button("✅ Создать и сгенерировать пароль")

            if submitted:
                if all([new_name, new_role, new_username]):
                    with st.spinner(f"Создание пользователя {new_name}..."):
                        response = api_client.create_user(
                            name=new_name, 
                            role=new_role, 
                            username=new_username,
                            password=None
                        )
                        if response:
                            st.success(f"Пользователь '{response.get('name')}' успешно создан!")
                            st.info(f"Сгенерированный пароль: **{response.get('generated_password')}**")
                            st.warning("Скопируйте этот пароль сейчас. После закрытия формы он не будет доступен.")
                else:
                    st.warning("Пожалуйста, заполните ФИО, Логин и Роль.")
    st.markdown("---")
    st.subheader("Управление существующими пользователями")
    all_users = api_client.get_all_users()
    if not all_users:
        st.info("В системе пока нет пользователей.")
    else:
        for user in all_users: user['delete'] = False
        edited_users_df = st.data_editor(all_users, column_config={"id": "ID", "name": "ФИО", "role": "Роль", "position": "Должность", "delete": st.column_config.CheckboxColumn("Удалить?", help="Отметьте для удаления")}, hide_index=True, key="user_editor", use_container_width=True)
        if st.button("🗑️ Применить удаление отмеченных", type="primary"):
            users_to_delete = [user for user in edited_users_df if user.get("delete")]
            if users_to_delete:
                progress_bar = st.progress(0, text="Начинаем удаление...")
                for i, user in enumerate(users_to_delete):
                    api_client.delete_user(user['id'])
                    st.toast(f"✅ Пользователь {user['name']} удален.")
                    progress_bar.progress((i + 1) / len(users_to_delete), text=f"Удалено {i+1} из {len(users_to_delete)}")
                st.rerun()
            else:
                st.info("Ни один пользователь не был отмечен для удаления.")

# =====================================================================================
# --- ГЛАВНЫЙ РОУТЕР ПРИЛОЖЕНИЯ ---
# =====================================================================================
if not st.session_state.logged_in:
    show_login_page()
else:
    st.sidebar.header(f"👤 {st.session_state.user_info.get('name')}")
    st.sidebar.caption(f"Роль: {st.session_state.user_info.get('role')}")
    if st.sidebar.button("Выйти", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_info = {}
        st.rerun()

    role = st.session_state.user_info.get("role")
    if role == "Работник":
        show_employee_page()
    elif role == "HR":
        show_hr_page()
    elif role == "Admin":
        show_admin_page()
    else:
        st.error("Неизвестная роль пользователя. Пожалуйста, войдите заново.")