import streamlit as st
import pandas as pd
from db import get_data_as_dataframe, sync_database
import os
LOG_FILE = "logs.txt"

st.header("База данных")

st.header("📝 Таблица игроков")
st.set_page_config(layout="wide")
df = get_data_as_dataframe()
filter_status = st.selectbox("Показать игроков со статусом:", ["Все", "Живой", "Мёртвый"])
if filter_status != "Все":
    df = df[df["status"] == filter_status]
def highlight_status(row):
    color = "green" if row["status"] == "Живой" else "red"
    return [f"background-color: {color}; color: white;" if col == "status" else "" for col in row.index]
styled_df = df.style.apply(highlight_status, axis=1)

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    column_config={
        "id": st.column_config.NumberColumn("ID", disabled=True), # Запрещаем редактировать ID
        "code": st.column_config.NumberColumn("ИНН", required=True),
        "name": st.column_config.TextColumn("Актер", required=False),
        "role_name": st.column_config.TextColumn("Название роли", required=True),
        "role": st.column_config.TextColumn("Роль", required=True),
        "description": st.column_config.TextColumn("Описание", required=True),
        "status": st.column_config.TextColumn("Статус", disabled=True),
    },
    use_container_width=True,
    key="data_editor"
)

if st.button("Сохранить изменения", type="primary"):
    try:
        # Вызываем функцию синхронизации, передавая ей измененный DataFrame
        sync_database(edited_df)
        st.success("Изменения успешно сохранены в базе данных! ✅")
        # Очищаем кэш, чтобы данные перезагрузились при следующем действии
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Произошла ошибка при сохранении: {e}")

st.markdown("---")
st.subheader("📜 Журнал озвученных фраз")

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = f.read()
        st.text_area("Лог (последние 20 строк):", "\n".join(logs.strip().splitlines()[-20:]), height=200,  disabled=True)
else:
    st.info("Пока ничего не озвучивалось.")