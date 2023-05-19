# создаем соединение с базой данных
import sqlite3
from sqlite3 import Error

from configs import db_name

conn = sqlite3.connect(db_name, check_same_thread=False)

# создаем курсор для работы с базой данных
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        lang TEXT NOT NULL,
        username TEXT NOT NULL,
        meta TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        job_id TEXT,
        reminder_text TEXT NOT NULL,
        reminder_date TEXT NOT NULL
    )
''')

# создаем таблицу для хранения списков задач
cursor.execute('''
    CREATE TABLE IF NOT EXISTS task_lists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        list_name TEXT NOT NULL,
        list_type TEXT NOT NULL
    )
''')

# сохраняем изменения
# conn.commit()

# создаем таблицу для хранения задач в списке задач
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        task_list_id INTEGER NOT NULL,
        task_text TEXT NOT NULL,
        task_deadline TEXT,
        task_status INTEGER NOT NULL
    )
''')

# сохраняем изменения
conn.commit()


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(db_name, check_same_thread=False)
        return conn
    except Error as e:
        print(e)

    return conn