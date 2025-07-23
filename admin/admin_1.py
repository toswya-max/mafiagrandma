import streamlit as st
from db import update_broadcast, get_broadcast
import base64
import io
import json
import os
import random
import time

st.set_page_config(layout="wide")

SONGS_FOLDER = "songs"
audio_paths = [os.path.join(SONGS_FOLDER, f) for f in os.listdir(SONGS_FOLDER) if f.endswith(".mp3")]
audio_bytes_list = []

st.header("🛠 Управление игрой")
current_message = get_broadcast()
st.markdown("---")
st.markdown("### 📔 Сообщение игрокам")
st.text_area("Текущее сообщение для игроков:", value=current_message, height=100, disabled=True)
new_msg = st.text_area("Новое сообщение", value=current_message)

if st.button("Обновить сообщение"):
    update_broadcast(new_msg)
    st.success("Сообщение обновлено!")
    st.rerun()
st.markdown("---")
st.markdown("### 📔 Кнопки управления")
col1, col2 = st.columns([1,1])
with col1:
    if st.button("Начать игру"):
        update_broadcast("Уважаемые игроки! \nИгра начинается, просим занять ваши места.")
        st.success("Уведомление отправлено")
        st.rerun()

with col2:
    if st.button("Закончить игру"):
        update_broadcast("Уважаемые игроки! \nСпасибо за игру, до скорой встречи!")
        st.success("Уведомление отправлено")
        st.rerun()

def create_full_playlist_player(list_of_audio_paths):
    playlist_data = []
    for path in list_of_audio_paths:
        try:
            with open(path, "rb") as f:
                b64_string = base64.b64encode(f.read()).decode()
                track_title = os.path.basename(path)
                playlist_data.append({
                    "src": f"data:audio/mp3;base64,{b64_string}",
                    "title": track_title
                })
        except FileNotFoundError:
            st.warning(f"Файл не найден и будет пропущен: {path}")
            continue 

    if not playlist_data:
        st.error("Не удалось загрузить ни одного трека для плейлиста.")
        return

    html_code = f"""
    <div style="font-family: sans-serif; border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; color: white;">
        <h4 style="margin-top: 0; color: white;">Плейлист</h4>
        <div id="current-track-title" style="font-weight: bold; margin-bottom: 10px; color: white;">-</div>

        <audio id="audio-player"></audio>

        <div style="display: flex; align-items: center; gap: 10px;">
            <button id="prev-btn" style="padding: 8px 12px; color: black;">⏮️</button>
            <button id="play-pause-btn" style="padding: 8px 12px; min-width: 120px; color: black;">Воспроизвести</button>
            <button id="next-btn" style="padding: 8px 12px; color: black;">⏭️</button>
        </div>
    </div>


    <script>
        const audioPlayer = document.getElementById('audio-player');
        const playPauseBtn = document.getElementById('play-pause-btn');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const trackTitle = document.getElementById('current-track-title');

        const playlist = {json.dumps(playlist_data)};
        let currentTrackIndex = 0;

        function loadTrack(index) {{
            if (index >= 0 && index < playlist.length) {{
                audioPlayer.src = playlist[index].src;
                trackTitle.textContent = playlist[index].title;
                currentTrackIndex = index;
            }}
        }}

        function playTrack() {{
            audioPlayer.play();
            playPauseBtn.textContent = 'Пауза';
        }}

        function pauseTrack() {{
            audioPlayer.pause();
            playPauseBtn.textContent = 'Воспроизвести';
        }}

        // Обработчики кнопок
        playPauseBtn.addEventListener('click', () => {{
            if (audioPlayer.paused) {{
                playTrack();
            }} else {{
                pauseTrack();
            }}
        }});

        nextBtn.addEventListener('click', () => {{
            const nextIndex = (currentTrackIndex + 1) % playlist.length; // Зацикливание плейлиста
            loadTrack(nextIndex);
            playTrack();
        }});

        prevBtn.addEventListener('click', () => {{
            const prevIndex = (currentTrackIndex - 1 + playlist.length) % playlist.length; // Зацикливание
            loadTrack(prevIndex);
            playTrack();
        }});

        // Автоматическое переключение на следующий трек
        audioPlayer.addEventListener('ended', () => {{
            nextBtn.click(); // Имитируем нажатие кнопки "Next"
        }});

        // Загружаем первый трек при инициализации
        loadTrack(0);
    </script>
    """
    
    # 3. Встраиваем компонент в Streamlit
    st.components.v1.html(html_code, height=150)

st.markdown("---")
st.markdown("### Фоновая музыка")

random.shuffle(audio_paths)

uploaded_files = st.file_uploader(
    "Загрузите один или несколько .mp3 файлов", 
    type=["mp3"], accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        save_path = os.path.join(SONGS_FOLDER, uploaded_file.name)
        # Перезаписываем файл, если такой есть
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.success(f"Загружено и сохранено {len(uploaded_files)} файлов в папку '{SONGS_FOLDER}'")
    
create_full_playlist_player(audio_paths)
