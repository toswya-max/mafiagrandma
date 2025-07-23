import streamlit as st
import requests
import os
import time
from io import BytesIO
from datetime import datetime
import base64
from db import get_players, get_role_game, kill_player
import sqlite3


# Игроки
players = [f"Игрок {i}" for i in range(1, 11)]
API_KEY = "sk_1fbde7edb20f942bdc900f1d9d1cf61f7e2e1a1d7b4c99cf"
VOICE_ID = "EMcrExxdKE2zz6aYnu5F"
MODEL_ID = "eleven_multilingual_v2"
LOG_FILE = "logs.txt"



# Состояния
if "mafia_target" not in st.session_state:
    st.session_state.mafia_target = None
if "doctor_target" not in st.session_state:
    st.session_state.doctor_target = None
if "sheriff_target" not in st.session_state:
    st.session_state.sheriff_target = None
if "night_result_shown" not in st.session_state:
    st.session_state.night_result_shown = False

def log_phrase(text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

def get_speech(text):
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.9,
            "similarity_boost": 0.9
        }
    }
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?optimize_streaming_latency=0"
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        log_phrase(text)
        return BytesIO(response.content)
    else:
        st.error(f"Ошибка генерации аудио: {response.status_code}")
        return None

def autoplay_audio(audio_bytes):
    b64 = base64.b64encode(audio_bytes.getvalue()).decode()
    audio_html = f"""
    <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

st.header("🌙 Ночная фаза")

def get_players_by_role(role):
    return [row for row in get_players() if row[4].lower() == role.lower()]

# Список ролей, для которых показываем кнопки выбора
special_roles = ["мафия", "доктор", "шериф"]

# Получаем игроков по ролям
mafia_players = get_players_by_role("мафия")
doctor_players = get_players_by_role("доктор")
sheriff_players = get_players_by_role("шериф")


st.subheader("🕵️ Действия ролей:")

col1, col2, col3 = st.columns(3)

all_players = get_players()
player_display_list = [f"{p[2]} | {p[3]}" for p in all_players]  # p[2] — name, p[3] — role_name

if 'selected1' not in st.session_state:
    st.session_state.selected1 = None
if 'selected2' not in st.session_state:
    st.session_state.selected2 = None

def on_select1():
    if st.session_state.selected1:
        st.session_state.selected2 = None  # сбросить выбор второго

def on_select2():
    if st.session_state.selected2:
        st.session_state.selected1 = None  # сбросить выбор первого

with col1:
    st.session_state.mafia_target = st.selectbox("Мафия выбирает", [""] + player_display_list)
    
with col2:
    st.session_state.doctor_target = st.selectbox("Доктор выбирает", [""] + player_display_list)

with col3:
    st.session_state.sheriff_target = st.selectbox("Шериф проверяет", [""] + player_display_list, key="selected1",
    on_change=on_select1)
    st.session_state.sheriff_kill = st.selectbox("или Шериф убивает", [""] + player_display_list, key="selected2",
    on_change=on_select2)

# === Подтверждение ===
if st.button("✅ Завершить ночь"):

    mafia = st.session_state.mafia_target
    doctor = st.session_state.doctor_target
    sheriff1 = st.session_state.sheriff_target
    sheriff2 = st.session_state.sheriff_kill
    if sheriff1:
        sheriff = sheriff1
    elif sheriff2:
        sheriff = sheriff2
    if not mafia or not doctor or not sheriff:
        st.warning("⚠️ Все роли должны выбрать цель!")
    else:
        st.session_state.night_result_shown = True



# === Результаты ночи ===
if st.session_state.night_result_shown:
    mafia = st.session_state.mafia_target
    doctor = st.session_state.doctor_target
    sheriff1 = st.session_state.sheriff_target
    sheriff2 = st.session_state.sheriff_kill
    if sheriff1:
        sheriff = sheriff1
    if sheriff2:
        sheriff = sheriff2
    st.markdown("---")
    st.subheader("📝 Итоги ночи")
    
    mafia, rolename = mafia.split(' | ')
    doctor, rolename1 = doctor.split(' | ')
    sheriff, rolename2 = sheriff.split(' | ')
    phrase = "Доброе утро, друзья! Давайте подводить итоги ночи."
    # Убит или нет
    if mafia == doctor:
        st.success("Никто не погиб — доктор спас цель мафии.")
        phrase += "Этой ночью никто не погиб."
    else:
        st.error(f"Мафия убил {rolename}")
        kill_player(rolename)
        phrase += f"Сегодня ночью погиб {rolename}."
    role = get_role_game(rolename2)[0]
    if sheriff1:
        st.info(f"🔍 Шериф проверил: {rolename2} — {role}")
        if role == "Доктор":
            role = "мирный"
        phrase += f"А также шериф проверил {rolename2}, он оказался {role}."
    elif sheriff2:
        if sheriff2 == doctor:
            st.success("Никто сегодня не умер благодаря доктору.")
            phrase += f"Если бы не доктор, то сегодня бы кто-то умер от рук шерифа."
        else:
            st.error(f"Шериф убил {rolename}")
            phrase += f"А также шериф убил {rolename2}, он оказался {role}."
    phrase += f"Чуть не забыл, наш доктор сегодня излечил {rolename1}. Всем удачного дня, надеюсь, каждый найдет выход!"

    # Озвучка
    if st.button("🔊 Озвучить итоги"):
        audio_bytes = get_speech(phrase)
        if audio_bytes is not None:
            autoplay_audio(audio_bytes)
        else:
            st.error("Не удалось получить аудио для воспроизведения.")


    # Кнопка сброса для следующей ночи
    if st.button("♻️ Следующая ночь"):
        for key in ["mafia_target", "doctor_target", "sheriff_target", "night_result_shown"]:
            st.session_state[key] = None
        st.rerun()
