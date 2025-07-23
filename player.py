import base64
import os
import json
import streamlit as st

def play_audio_queue(voicing_path, music_path):
    # Кодирование озвучки
    with open(voicing_path, "rb") as f:
        voicing_b64 = base64.b64encode(f.read()).decode()
    # Кодирование музыки
    with open(music_path, "rb") as f:
        music_b64 = base64.b64encode(f.read()).decode()

    # HTML и JS
    html = f"""
    <script>
        if (window.audioPlayer) {{
            window.audioPlayer.pause();
            window.audioPlayer.currentTime = 0;
        }}

        // Очередь аудиофайлов
        const voicing = new Audio("data:audio/mp3;base64,{voicing_b64}");
        const music = new Audio("data:audio/mp3;base64,{music_b64}");

        // Сохраняем глобальную ссылку
        window.audioPlayer = voicing;

        // После озвучки — запуск музыки
        voicing.addEventListener('ended', () => {{
            window.audioPlayer = music;
            music.play();
        }});

        voicing.play();
    </script>
    """
    st.components.v1.html(html, height=0)