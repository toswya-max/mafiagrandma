import streamlit as st
from db import init_db, set_player, find

init_db()

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None, "Игрок", "Админ"]

def login():
    st.header("Log in")
    role = st.selectbox("Выбери свою роль", ROLES)
    if role == "Игрок":
        st.subheader("Вход для Игрока")
        code = st.text_input("Введите код игры")
        name = st.text_input("Введи ваше имя")
        if st.button("Войти как Игрок"):
            if code and name:
                st.session_state.player_code = code
                st.session_state.player_name = name
                if find(code) is None:
                    st.error("Не нашли такого пользователя! Повтори попытку.")
                else:
                    set_player(code, name)
                    st.session_state.role = role
                    st.rerun()
                    st.success("Вы вошли как игрок")
            else:
                st.warning("Введите код и имя")
    
    elif role == "Админ":
        code = st.text_input("Введите код доступа")
        if st.button("Войти как Админ"):
            if code == "rvc":
                st.session_state.role = role
                st.rerun()
                st.success("Вы вошли как админ")
            else:
                st.error("Неправильный код! Повтори попытку.")
        

role = st.session_state.role

if "role" not in st.session_state:
    st.session_state.role = None
if "player_code" not in st.session_state:
    st.session_state.player_code = ""
if "player_name" not in st.session_state:
    st.session_state.player_name = ""

request_1 = st.Page(
    "request/request_1.py",
    title="Основная игра",
    icon=":material/help:",
    default=(role == "Игрок"),
)
admin_1 = st.Page(
    "admin/admin_1.py",
    title="Настройка игры",
    icon=":material/security:",
    default=(role == "Admin"),
)
admin_2 = st.Page("admin/admin_2.py", title="Основные действия", icon=":material/person_add:")
admin_3 = st.Page("admin/admin_3.py", title="База данных", icon=":material/table_chart:")
# admin_4 = st.Page("admin/admin_4.py", title="Проверка", icon=":material/table_chart:")
# admin_5 = st.Page("admin/admin_5.py", title="озвучка", icon=":material/table_chart:")

request_pages = [request_1]
admin_pages = [admin_1, admin_2, admin_3]

##################

st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")
if role is None:
    # Если роль не установлена (None), показываем только страницу входа
    pg = st.navigation([st.Page(login, title="Войти", default=True)])
else:
    page_dict = {}
    if st.session_state.role in ["Игрок", "Админ"]:
        page_dict["Игрок"] = request_pages
    if st.session_state.role == "Админ":
        page_dict["Админ"] = admin_pages
    if page_dict:
        pg = st.navigation(page_dict)
    else:
        pg = st.navigation([st.Page(login)])

###################

pg.run()