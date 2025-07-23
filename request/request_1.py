import streamlit as st
from db import get_broadcast, get_role, get_desc
import time
st.set_page_config(layout="wide")
role = st.session_state.player_code
if st.session_state.role == "Игрок":
    st.header(f"👋 Привет, **{st.session_state.player_name}**!")
    st.write(f"Твоя роль - **{get_role(role)[0]}**. Пока ожидаешь игру, можешь ознакомится со своей историей.")
    st.markdown("---")
    st.markdown("### 📔 Твоя история")
    st.write(f"{get_desc(role)[0]}")
else: 
    st.header("👋 Привет, ***!")

message = get_broadcast()
st.markdown("---")
st.markdown("### 🔔 Сообщение от ведущего:")
st.info(message or "Пока нет сообщений.")
if message == "Уважаемые игроки! Игра начинается, просим занять ваши места.":
    st.balloons()
else:
    while message != "Уважаемые игроки! Игра начинается, просим занять ваши места.":
        time.sleep(5)
        st.rerun()