import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            name TEXT,
            role_name TEXT, 
            role TEXT,
            description TEXT,
            status TEXT DEFAULT 'Живой'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS broadcast (
            id INTEGER PRIMARY KEY,
            message TEXT
        )
    ''')
    # Инициализируем пустое сообщение (если нет)
    c.execute("INSERT OR IGNORE INTO broadcast (id, message) VALUES (1, '')")
    conn.commit()
    conn.close()

def get_players():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM players")  # id, code, name, role_name, role, description
    rows = c.fetchall()
    conn.close()
    return rows

def get_players_by_role(role):
    players = []
    for row in get_players():
        # row — кортеж, извлекаем нужные поля по индексам
        # Например, name — 2, role — 4, role_name — 3
        if row[4] == role:  
            players.append({
                "id": row[0],
                "code": row[1],
                "name": row[2],
                "role_name": row[3],
                "description": row[5],
            })
    return players

def get_alive_players():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name, role_name FROM players WHERE status = ?", ("Живой",))
    rows = c.fetchall()
    conn.close()
    return rows


def add_player(code, name):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO players (code, name, role) VALUES (?, ?, 'Игрок')", (code, name))
    conn.commit()
    conn.close()

def set_player(code, name):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE players SET name = ? WHERE code = ?", (name, code))
    conn.commit()
    conn.close()

def find(code):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE code = ?", (code,))
    result = c.fetchone()
    return 1 if result else None

def get_role(code):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT role FROM players WHERE code = ?",
        (code,)
    )
    return cursor.fetchone()

def get_role_game(code):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT role FROM players WHERE role_name = ?",
        (code,)
    )
    return cursor.fetchone()

def get_desc(code):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT description FROM players WHERE code = ?",
        (code,)
    )
    return cursor.fetchone()

def get_broadcast():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT message FROM broadcast WHERE id = 1")
    msg = c.fetchone()[0]
    conn.close()
    return msg

def update_broadcast(new_msg):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE broadcast SET message = ? WHERE id = 1", (new_msg,))
    conn.commit()
    conn.close()

def get_players_as_dicts():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row  # возвращает строки как словари
    cursor = conn.cursor()
    cursor.execute("SELECT code, name, role, description FROM players")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_db_connection():
    """Создает подключение к базе данных."""
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row # Позволяет обращаться к колонкам по имени
    return conn


def get_data_as_dataframe():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM players", conn)
    conn.close()
    return df

def sync_database(df):
    """Синхронизирует состояние DataFrame с базой данных."""
    conn = get_db_connection()
    cursor = conn.cursor()
    db_ids = set(pd.read_sql_query("SELECT id FROM players", conn)['id'])
    df_ids = set(df['id'].dropna()) 

    ids_to_delete = db_ids - df_ids
    if ids_to_delete:
        cursor.executemany("DELETE FROM players WHERE id = ?", [(id,) for id in ids_to_delete])

    # 2. Обновление и добавление строк
    for _, row in df.iterrows():
        if pd.notna(row['id']) and int(row['id']) in db_ids:
            cursor.execute(
                "UPDATE players SET code = ?, name = ?, role_name = ?, role = ?, description = ? WHERE id = ?",
                (row['code'], row['name'], row['role_name'], row['role'], row['description'], int(row['id']))
            )
        elif pd.isna(row['id']):
            cursor.execute(
                "INSERT INTO players (code, name, role_name, role, description, status) VALUES (?, ?, ?, ?, ?, ?)",
                (row['code'], row['name'], row['role_name'], row['role'], row['description'], "Живой",)
            )
            
    conn.commit()
    conn.close()

def kill_player(role):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE players SET status = ? WHERE role = ?", ("Мертвый", role,))