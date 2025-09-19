import streamlit as st
import api_client # Наш модуль для общения с FastAPI

# --- Конфигурация страницы ---
st.set_page_config(
    layout="wide",
    page_title="Talent Navigator AI",
    page_icon="🚀"
)

# --- Инициализация состояния сессии ---
# Это "память" приложения, которая сохраняется между действиями пользователя.
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
            username = st.text_input("Имя пользователя", help="Для демо используйте: employee, hr, admin")
            password = st.text_input("Пароль", type="password", help="Для демо используйте: employee, hr, admin")
            
            submitted = st.form_submit_button("Войти", use_container_width=True, type="primary")

            if submitted:
                with st.spinner("Аутентификация..."):
                    user_data = api_client.login(username, password)
                    if user_data and user_data.get("success"):
                        st.session_state.logged_in = True
                        st.session_state.user_info = user_data
                        st.rerun() # Перезапускаем скрипт, чтобы показать основной интерфейс
                    # Сообщение об ошибке выводится внутри api_client

# =====================================================================================
# --- СТРАНИЦА РАБОТНИКА ---
# =====================================================================================
def show_employee_page():
    """Отрисовывает интерфейс для сотрудника."""
    st.title(f"👋 Привет, {st.session_state.user_info.get('name')}!")
    st.caption("Это ваш личный карьерный навигатор. Здесь вы можете отслеживать свой прогресс, строить планы развития и получать предложения о новых ролях.")
    st.markdown("---")

    tab_profile, tab_plan, tab_offers = st.tabs([
        "👤 Мой профиль", 
        "🗺️ Карьерный план", 
        "📬 Офферы"
    ])

    with tab_profile:
        user_id = st.session_state.user_info.get('user_id')
        
        @st.cache_data(ttl=60)
        def get_profile_data(uid):
            return api_client.get_user_profile(uid), api_client.get_user_progress(uid)

        profile_data, gamification_data = get_profile_data(user_id)

        if not profile_data or not gamification_data:
            st.error("Не удалось загрузить данные профиля. Попробуйте обновить страницу.")
        else:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(profile_data.get("photo_url", ""), use_container_width=True, caption=profile_data.get("nickname"))
            with col2:
                st.header(profile_data.get("name"))
                st.subheader(profile_data.get("position"))
                st.markdown(f"**Обо мне:** *{profile_data.get('about')}*")
            
            st.markdown("---")
            st.subheader("Ваш прогресс")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("✨ Очки опыта (XP)", gamification_data.get('xp', 0))
            with col2:
                st.metric("🚀 Уровень", f"Lvl {gamification_data.get('level', 1)}")

            achievements = gamification_data.get('achievements', [])
            if achievements:
                st.write("**Полученные достижения:** " + " ".join([f"🏆 `{ach}`" for ach in achievements]))

            st.markdown("---")
            st.subheader("Ключевые навыки")
            skills = profile_data.get("skills", [])
            if skills:
                st.info(" ".join([f"`{skill.upper()}`" for skill in skills]))
            else:
                st.warning("Вы еще не добавили ни одного навыка.")

            with st.expander("⚙️ Настройки профиля"):
                st.toggle("Скрыть карьерный путь от коллег", value=profile_data.get('career_path_visible', True))
                st.toggle("Показывать мой уровень в профиле", value=profile_data.get('level_visible', True))
                st.toggle("Показывать мои достижения", value=profile_data.get('achievements_visible', True))
                if st.button("Сохранить настройки", type="secondary"):
                    st.toast("Настройки сохранены (симуляция)")

    with tab_plan:
        st.header("🤖 Ваш персональный ИИ-консультант")
        st.info("Нажмите на кнопку ниже, чтобы наш ИИ проанализировал ваш профиль, навыки и цели, и построил персональный план развития внутри компании.")

        if st.button("🚀 Построить мой карьерный путь", type="primary", use_container_width=True):
            user_id = st.session_state.user_info.get('user_id')
            with st.spinner("🧠 ИИ-консультант анализирует ваш профиль... Это может занять до 30 секунд."):
                plan = api_client.generate_career_plan(user_id)

            if plan:
                st.balloons()
                st.subheader("✅ Ваш персональный план готов!")
                
                with st.container(border=True):
                    st.markdown("### 🔍 Анализ текущей роли")
                    st.success(plan.get("current_analysis", "Нет данных."))
                with st.container(border=True):
                    st.markdown("### 🧭 Рекомендуемый следующий шаг")
                    path = plan.get("recommended_path", {})
                    st.info(f"**Целевая роль:** {path.get('target_role', 'Не определена')}\n\n"
                            f"**Почему она вам подходит:** {path.get('why_it_fits', 'Нет данных.')}")
                with st.container(border=True):
                    st.markdown("### 🎯 Навыки для развития (Skill Gap)")
                    skill_gap = plan.get("skill_gap", [])
                    if skill_gap:
                        for gap in skill_gap:
                            st.markdown(f"- **`{gap.get('skill')}`** — {gap.get('reason')}")
                with st.container(border=True):
                    st.markdown("### 📝 План действий")
                    action_steps = plan.get("actionable_steps", [])
                    if action_steps:
                        for step in action_steps:
                            st.markdown(f"**Шаг {step.get('step')} ({step.get('type')}):** {step.get('description')}")

    with tab_offers:
        st.header("📬 Ваши предложения")
        st.info("Здесь отображаются приглашения от HR-специалистов на участие в новых проектах или переход на новые должности.")
        fake_offers = [{"hr_name": "Петр Петров", "vacancy": "Middle Python Developer", "status": "Новое"}]
        for i, offer in enumerate(fake_offers):
            with st.container(border=True):
                col1, col2 = st.columns([3,1])
                with col1:
                    st.subheader(offer['vacancy'])
                    st.caption(f"От: {offer['hr_name']}")
                with col2:
                    st.info(f"Статус: {offer['status']}")
                    if st.button("👁️ Посмотреть", key=f"view_{i}"):
                        st.toast(f"Просмотр оффера '{offer['vacancy']}' (симуляция)")

# =====================================================================================
# --- СТРАНИЦА HR ---
# =====================================================================================
def show_hr_page():
    st.title(f"📇 Панель HR-специалиста, {st.session_state.user_info.get('name')}")
    st.caption("Используйте умный поиск для нахождения идеальных кандидатов на основе их опыта и навыков.")
    st.markdown("---")

    tab_search, tab_my_offers = st.tabs(["🔍 Поиск кандидатов", "📄 Мои офферы"])

    with tab_search:
        st.header("🧠 Умный поиск кандидатов")
        st.info("Опишите задачу или роль своими словами. Например: 'Нужен опытный разработчик на Python со знанием облачных технологий для нового проекта'. ИИ найдет самых релевантных сотрудников.")
        with st.form("search_form"):
            search_prompt = st.text_area("Описание идеального кандидата:", height=150)
            submitted = st.form_submit_button("Найти кандидатов", type="primary", use_container_width=True)
            if submitted and search_prompt:
                with st.spinner("ИИ анализирует профили сотрудников..."):
                    results = api_client.match_candidates(search_prompt)
                st.subheader("🏆 Результаты поиска:")
                if not results:
                    st.warning("Не найдено подходящих кандидатов по вашему запросу.")
                else:
                    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
                    for result in sorted_results:
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.subheader(result.get("name"))
                                st.caption(f"Должность: {result.get('position')}")
                            with col2:
                                match_percent = int(result.get('score', 0) * 100)
                                st.progress(match_percent, text=f"Релевантность: {match_percent}%")
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("Посмотреть профиль", key=f"view_{result.get('user_id')}", use_container_width=True):
                                    st.toast(f"Просмотр профиля {result.get('name')} (симуляция)")
                            with c2:
                                if st.button("Отправить оффер", key=f"offer_{result.get('user_id')}", use_container_width=True, type="secondary"):
                                    st.toast(f"Отправка оффера {result.get('name')} (симуляция)")
            elif submitted:
                st.warning("Пожалуйста, введите описание для поиска.")

    with tab_my_offers:
        st.header("📄 Отслеживание отправленных офферов")
        fake_sent_offers = [{"candidate_name": "Иван Иванов", "vacancy": "Middle Python Developer", "sent_at": "2024-09-18 15:30", "status": "Просмотрено"}]
        st.data_editor(fake_sent_offers, column_config={"candidate_name": "Кандидат", "vacancy": "Вакансия", "sent_at": "Отправлено", "status": "Статус"}, hide_index=True, use_container_width=True, disabled=True)

# =====================================================================================
# --- СТРАНИЦА АДМИНА ---
# =====================================================================================
def show_admin_page():
    st.title("🛠️ Панель администратора")
    with st.expander("Создать нового пользователя", expanded=False):
        with st.form("create_user_form", clear_on_submit=True):
            st.subheader("Данные нового пользователя")
            new_name = st.text_input("ФИО")
            new_role = st.selectbox("Роль", ["Работник", "HR"], index=0)
            submitted = st.form_submit_button("✅ Создать пользователя")
            if submitted and new_name and new_role:
                with st.spinner(f"Создание пользователя {new_name}..."):
                    response = api_client.create_user(name=new_name, role=new_role)
                    if response:
                        st.success(f"Пользователь '{response.get('name')}' успешно создан с ID {response.get('user_id')}!")
            elif submitted:
                st.warning("Пожалуйста, заполните все поля.")
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
                st.experimental_rerun()
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