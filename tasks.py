from telebot import types

from configs import bot, texts
from db import cursor, conn
from user import get_lang


def add_task(message):
    user_id = message.chat.id
    cursor.execute("SELECT DISTINCT list_name FROM task_lists WHERE user_id=?", (user_id,))
    lists = cursor.fetchall()

    if lists:
        message = texts['select_list_for_create_task'][get_lang(user_id)]
        keyboard = types.InlineKeyboardMarkup()
        for task_list in lists:
            keyboard.add(types.InlineKeyboardButton(task_list[0], callback_data=f"listToAddTask_{task_list[0]}"))

        bot.send_message(chat_id=user_id, text=message, reply_markup=keyboard)
    else:
        bot.reply_to(message, texts['no_lists_warn'][get_lang(user_id)])


def add_task_step3(message, list_name):
    user_id = message.chat.id
    task = message.text

    cursor.execute("SELECT id FROM task_lists WHERE user_id=? AND list_name=?", (user_id, list_name))
    list_id = cursor.fetchone()
    cursor.execute("INSERT INTO tasks (user_id, task_list_id, task_text, task_deadline, task_status) VALUES (?, ?, ?, ?, 0)", (user_id, list_id[0], task, 'no'))
    conn.commit()
    bot.reply_to(message, f'{texts["task_added_in_list"][get_lang(user_id)]} {list_name}:\n{task}', parse_mode='Markdown')


def get_tasks(user_id, list_name):
    cursor.execute("SELECT id FROM task_lists WHERE user_id=? AND list_name=?", (user_id, list_name))
    list_id = cursor.fetchone()

    cursor.execute("SELECT id, task_text, task_status, task_deadline FROM tasks WHERE user_id=? AND task_list_id = ?", (user_id, list_id[0],))
    tasks = cursor.fetchall()

    return tasks


def get_task(task_id, user_id):
    cursor.execute("SELECT task_text, task_status, task_deadline FROM tasks WHERE id=?", (task_id,))
    task = cursor.fetchone()

    task = list(task)
    task[0] = f"{task[0]}\n\n{texts['status'][get_lang(user_id)]}: {task[1]}"
    return task


def delete_task(task_id):
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()


def update_task_status(task_id, new_status):
    cursor.execute("UPDATE tasks SET task_status = ? WHERE id = ?", (new_status, task_id,))
    conn.commit()