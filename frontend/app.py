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
            username = st.text_input("Имя пользователя")
            password = st.text_input("Пароль", type="password")
            
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
    st.title(f"👋 Привет, {st.session_state.user_info.get('name')}!")
    st.caption("Это ваш личный карьерный навигатор. Здесь вы можете отслеживать свой прогресс, строить планы развития и получать предложения о новых ролях.")
    st.markdown("---")

    tab_profile, tab_plan, tab_offers = st.tabs(["👤 Мой профиль", "🗺️ Карьерный план", "📬 Офферы"])

    with tab_profile:
        user_id = st.session_state.user_info.get('user_id')
        
        @st.cache_data(ttl=5) 
        def get_profile_data(uid):
            profile = api_client.get_user_profile(uid)
            gamification = api_client.get_user_progress(uid)
            return profile, gamification
        
        if "edit_mode" not in st.session_state:
            st.session_state.edit_mode = False

        # --- Кнопка для переключения в режим редактирования ---
        # Если мы не в режиме редактирования, показываем кнопку
        if not st.session_state.edit_mode:
            if st.button("✏️ Редактировать профиль"):
                st.session_state.edit_mode = True
                st.rerun()

        # --- НАДЕЖНАЯ ФОРМА РЕДАКТИРОВАНИЯ (без st.dialog) ---
        # Эта форма будет появляться прямо на странице, когда edit_mode == True
        if st.session_state.edit_mode:
            with st.container(border=True):
                st.subheader("Редактирование профиля")
                profile_data_to_edit, _ = get_profile_data(user_id)
                
                with st.form("edit_profile_form"):
                    nickname_val = profile_data_to_edit.get("nickname", "")
                    about_val = profile_data_to_edit.get("about", "")
                    skills_list = profile_data_to_edit.get("skills", [])
                    skills_val = ", ".join(skills_list)

                    new_nickname = st.text_input("Никнейм", value=nickname_val)
                    new_about = st.text_area("Обо мне", value=about_val, height=150)
                    new_skills_str = st.text_input("Навыки (через запятую)", value=skills_val)

                    col1, col2 = st.columns([1,1])
                    with col1:
                        if st.form_submit_button("Сохранить", use_container_width=True, type="primary"):
                            new_skills_list = [skill.strip() for skill in new_skills_str.split(",") if skill.strip()]
                            
                            with st.spinner("Сохранение..."):
                                api_client.update_user_profile(user_id, new_nickname, new_about, new_skills_list)
                            
                            st.toast("Профиль успешно обновлен!")
                            st.session_state.edit_mode = False
                            st.rerun()
                    with col2:
                        if st.form_submit_button("Отмена", use_container_width=True):
                            st.session_state.edit_mode = False
                            st.rerun()

        # --- Отображение профиля (основная часть) ---
        # Этот блок будет виден всегда, даже во время редактирования, что может быть удобно
        profile_data, gamification_data = get_profile_data(user_id)

        if not profile_data or not gamification_data:
            st.error("Не удалось загрузить данные профиля.")
        else:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(profile_data.get("photo_url", ""), use_container_width=True, caption=profile_data.get("nickname"))
            with col2:
                st.header(profile_data.get("name"))
                st.subheader(profile_data.get("position", "Должность не указана"))
                st.markdown(f"**Обо мне:** *{profile_data.get('about', 'Информация не заполнена')}*")
            st.markdown("---")
            st.subheader("Ключевые навыки")
            skills = profile_data.get("skills", [])
            if skills:
                st.info(" ".join([f"`{skill.upper()}`" for skill in skills]))
            else:
                st.warning("Вы еще не добавили ни одного навыка. Нажмите 'Редактировать профиль', чтобы добавить их.")
            
            st.markdown("---")
            st.subheader("Ваш прогресс")
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                st.metric("✨ Очки опыта (XP)", gamification_data.get('xp', 0))
            with g_col2:
                st.metric("🚀 Уровень", f"Lvl {gamification_data.get('level', 1)}")

            achievements = gamification_data.get('achievements', [])
            if achievements:
                st.write("**Полученные достижения:** " + " ".join([f"🏆 `{ach}`" for ach in achievements]))
            
            with st.expander("⚙️ Настройки профиля"):
                st.toggle("Скрыть карьерный путь", value=True)
                st.toggle("Показывать мой уровень", value=True)
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
        user_id = st.session_state.user_info.get('user_id')
        offers = api_client.get_user_offers(user_id)

        if offers is None:
            st.error("Не удалось загрузить офферы.")
        elif not offers:
            st.success("У вас пока нет новых предложений. Отличная работа!")
        else:
            for offer in offers:
                with st.container(border=True):
                    # Получаем имя HR для отображения
                    hr_profile = api_client.get_user_profile(offer['from_hr_id'])
                    hr_name = hr_profile.get('name') if hr_profile else "Неизвестный HR"

                    st.subheader(offer['title'])
                    st.caption(f"От: {hr_name}")
                    st.info(f"Статус: {offer['status']}")
                    
                    with st.expander("Показать описание"):
                        st.write(offer['description'])

                    # Не показываем кнопки, если статус уже изменен
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
        hr_id = st.session_state.user_info.get('user_id')
        sent_offers = api_client.get_hr_offers(hr_id)

        if sent_offers is None:
            st.error("Не удалось загрузить отправленные офферы.")
        elif not sent_offers:
            st.info("Вы еще не отправили ни одного оффера.")
        else:
            # Готовим данные для таблицы
            display_data = []
            for offer in sent_offers:
                user_profile = api_client.get_user_profile(offer['to_user_id'])
                user_name = user_profile.get('name') if user_profile else "Неизвестный сотрудник"
                display_data.append({
                    "candidate_name": user_name,
                    "vacancy": offer['title'],
                    "sent_at": offer.get('timestamp', '').strip('"'),
                    "status": offer['status']
                })

            st.data_editor(
                display_data,
                column_config={
                    "candidate_name": "Кандидат", "vacancy": "Вакансия", 
                    "sent_at": "Отправлено", "status": "Статус"
                },
                hide_index=True, use_container_width=True, disabled=True
            )

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
                        # Вызываем api_client без пароля
                        response = api_client.create_user(
                            name=new_name, 
                            role=new_role, 
                            username=new_username,
                            password=None # Передаем None, чтобы бэкенд сгенерировал пароль
                        )
                        if response:
                            st.success(f"Пользователь '{response.get('name')}' успешно создан!")
                            # Показываем сгенерированный пароль
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