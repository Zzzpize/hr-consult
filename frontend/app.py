import streamlit as st
import api_client

st.set_page_config(layout="wide", page_title="HR Navigator AI", page_icon="🚀")

# --- Инициализация состояния сессии ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = {}

# --- Функции для отрисовки страниц ---

def show_login_page():
    st.title("Добро пожаловать в Talent Navigator AI!")
    
    with st.form("login_form"):
        username = st.text_input("Имя пользователя (employee, hr, admin)")
        password = st.text_input("Пароль (employee, hr, admin)", type="password")
        submitted = st.form_submit_button("Войти")

        if submitted:
            user_data = api_client.login(username, password)
            if user_data and user_data.get("success"):
                st.session_state.logged_in = True
                st.session_state.user_info = user_data
                st.rerun() # Перезапускаем скрипт, чтобы показать основной интерфейс

def show_employee_page():
    st.title(f"👋 Привет, {st.session_state.user_info.get('name')}!")
    st.write("Это ваш личный карьерный навигатор.")
    # TODO: Добавить st.tabs для профиля, чат-бота, офферов

def show_hr_page():
    st.title(f"Панель HR-специалиста, {st.session_state.user_info.get('name')}")
    # TODO: Добавить st.tabs для поиска и офферов

def show_admin_page():
    st.title("🛠️ Панель администратора")
    # TODO: Добавить логику отображения и управления пользователями
    st.write("Здесь будет управление пользователями.")
    users = api_client.get_all_users()
    st.dataframe(users) # Простой вывод списка пользователей

# --- Главный роутер приложения ---

if not st.session_state.logged_in:
    show_login_page()
else:
    # Добавляем кнопку выхода в сайдбар
    st.sidebar.header(f"Роль: {st.session_state.user_info.get('role')}")
    if st.sidebar.button("Выйти"):
        st.session_state.logged_in = False
        st.session_state.user_info = {}
        st.rerun()

    # Определяем, какую страницу показать
    role = st.session_state.user_info.get("role")
    if role == "Работник":
        show_employee_page()
    elif role == "HR":
        show_hr_page()
    elif role == "Admin":
        show_admin_page()
    else:
        st.error("Неизвестная роль пользователя.")