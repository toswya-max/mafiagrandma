import streamlit as st
import requests
import base64
from io import BytesIO

# 🔐 Вставь свой API-ключ и ID голоса
API_KEY = "sk_f6f79d7713fa2b2debcd84318952d045fa525c82a2744d4a"
VOICE_ID = "ywL1GEe9JbaEqINm2Qdt"
MODEL_ID = "eleven_multilingual_v2"

def get_audio(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 0.8
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"Ошибка {response.status_code}: {response.text}")
        return None

# 💾 Сохранить MP3
def save_audio_to_file(audio_bytes, filename):
    with open(filename, "wb") as f:
        f.write(audio_bytes)

# 🔊 Воспроизведение MP3-файла в браузере
def autoplay_audio_from_file(filepath):
    with open(filepath, "rb") as f:
        audio_bytes = BytesIO(f.read())
    b64 = base64.b64encode(audio_bytes.getvalue()).decode()
    audio_html = f"""
        <audio autoplay controls>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# 📋 Интерфейс
st.title("🎙️ Генератор и проигрыватель озвучек для Мафии")

text = st.text_input("Введите фразу:")
filename = st.text_input("Имя для файла (без .mp3)", value="voice")

if st.button("Сгенерировать, сохранить и воспроизвести"):
    if not text.strip():
        st.warning("Введите текст.")
    else:
        audio_bytes = get_audio(text)
        if audio_bytes:
            file_path = f"{filename}.mp3"
            save_audio_to_file(audio_bytes, file_path)
            st.success(f"Сохранено как {file_path}")
            autoplay_audio_from_file(file_path)
