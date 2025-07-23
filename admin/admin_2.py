import streamlit as st
import requests
import os
import time
from io import BytesIO
from datetime import datetime
import base64
from db import get_players, get_role_game, get_alive_players, kill_player
from player import play_audio_queue

# ====== Константы ======
API_KEY = "sk_e8f4153f03971e876a5e4f47392f3da2371ee3d837298d8c"
VOICE_ID = "ywL1GEe9JbaEqINm2Qdt"
MODEL_ID = "eleven_multilingual_v2"
LOG_FILE = "logs.txt"

# ====== Настройки страницы ======
st.set_page_config(layout="wide")

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
        <audio autoplay id="my-audio" style="display:none">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            const audio = document.getElementById("my-audio");
            if (audio) {{
                audio.play().catch(e => console.log(e));
            }}
        </script>
    """
    st.components.v1.html(audio_html, height=0)

# ====== Интерфейс ======

st.header("🌙 Ночная фаза")

st.subheader("🗣 Быстрые фразы")

def audio(mp3_path):
    with open(mp3_path, "rb") as f:
        audio_data = f.read()
        return audio_data

co1, co2, co3, co4, co5 = st.columns(5)
with co1:
    if st.button("Начать игру"):
        audio_mp3 = "mafia/history.mp3"
        audio_bytes = BytesIO(audio(audio_mp3))
        play_audio_queue(audio_mp3, "songs/background.mp3")
    if st.button("Победила мафия"):
        audio_mp3 = "songs/background.mp3"
        audio_bytes = BytesIO(audio(audio_mp3))
        autoplay_audio(audio_bytes)
    if st.button("Победили мирные"):
        audio_mp3 = "songs/Jann - Arachnophobia.mp3"
        audio_bytes = BytesIO(audio(audio_mp3))
        autoplay_audio(audio_bytes)

with co2:
    if st.button("Город засыпает"):
        audio_mp3 = "mafia/city_1.mp3"
        audio_bytes = BytesIO(audio(audio_mp3))
        
        autoplay_audio(audio_bytes)
    if st.button("Город просып."):
        audio_mp3 = "mafia/city_2.mp3"
        audio_bytes = BytesIO(audio(audio_mp3))
        autoplay_audio(audio_bytes)

with co3:
    if st.button("Мафия просып."):
        audio_mp3 = "mafia/mafia_1.mp3"
        audio_bytes = BytesIO(audio(audio_mp3))
        autoplay_audio(audio_bytes)
    if st.button("Мафия засыпает"):
        audio_mp3 = "mafia/mafia_2.mp3"
        audio_bytes = BytesIO(audio(audio_mp3))
        autoplay_audio(audio_bytes)

with co4:
    if st.button("Доктор просып."):
        audio_mp3 = "mafia/doctor_1.mp3"
        audio_bytes = BytesIO(audio(audio_mp3))
        autoplay_audio(audio_bytes)
    if st.button("Доктор засыпает"):
        audio_mp3 = "mafia/doctor_2.mp3"
        audio_bytes = BytesIO(audio(audio_mp3))
        autoplay_audio(audio_bytes)

with co5:
    if st.button("Шериф просып."):
        audio_mp3 = "mafia/sherif_1.mp3"
        audio_bytes = BytesIO(audio(audio_mp3))
        autoplay_audio(audio_bytes)
    if st.button("Шериф засыпает"):
        audio_mp3 = "mafia/sherif_2.mp3"
        audio_bytes = BytesIO(audio(audio_mp3))
        autoplay_audio(audio_bytes)

st.markdown("---")
def get_players_by_role(role):
    return [row for row in get_players() if row[4].lower() == role.lower()]

# Список ролей, для которых показываем кнопки выбора
special_roles = ["мафия", "доктор", "шериф"]

# Получаем игроков по ролям
mafia_players = get_players_by_role("мафия")
doctor_players = get_players_by_role("доктор")
sheriff_players = get_players_by_role("шериф")


st.subheader("🕵️ Действия ролей:")


alive_players = get_alive_players()
if alive_players:
    with st.form(key="night_form"):
        col1, col2, col3 = st.columns(3)
        player_names = [f"{row['name']} | {row['role_name']}" for row in alive_players]

        with col1:
            mafia_select = st.selectbox("Мафия выбирает", [""] + player_names)
        with col2:
            doctor_select = st.selectbox("Доктор выбирает", [""] + player_names)
        with col3:
            sheriff_select = st.selectbox("Шериф проверяет", [""] + player_names)
            sheriff_kill = st.selectbox("или Шериф убивает", [""] + player_names)

        submitted = st.form_submit_button("✅ Завершить ночь")
else:
    st.warning("Нет живых игроков.")

if submitted:
    if sheriff_select and sheriff_kill:
        st.warning("⚠️ Шериф может выбрать только одно действие: проверить или убить.")
    elif not mafia_select or not doctor_select or not (sheriff_select or sheriff_kill):
        st.warning("⚠️ Все роли должны выбрать цель!")
    else:
        st.session_state.mafia_target = mafia_select
        st.session_state.doctor_target = doctor_select
        st.session_state.sheriff_target = sheriff_select
        st.session_state.sheriff_kill = sheriff_kill
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
        st.error(f"Погиб {rolename}")
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
            st.error(f"Шериф убил {rolename2}")
            kill_player(rolename2)
            phrase += f"А также шериф убил {rolename2}, он оказался {role}."
    phrase += f"Чуть не забыл, наш доктор сегодня излечил {rolename1}. Всем удачного дня, надеюсь, каждый найдет выход!"

    # Озвучка
    if st.button("🔊 Озвучить итоги"):
        audio_bytes = get_speech(phrase)
        autoplay_audio(audio_bytes)

    # Кнопка сброса для следующей ночи
    if st.button("♻️ Следующая ночь"):
        for key in ["mafia_target", "doctor_target", "sheriff_target", "night_result_shown"]:
            st.session_state[key] = None
        st.rerun()

