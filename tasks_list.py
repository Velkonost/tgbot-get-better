from telebot import types

from configs import bot, texts, items_per_page
from db import cursor, conn
from user import get_lang


def get_task_lists(user_id):
    cursor.execute("SELECT list_name, id FROM task_lists WHERE user_id=?", (user_id,))
    task_lists = cursor.fetchall()

    return task_lists


def add_task_list(message):
    task_list_name = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    task_list_type = "current"

    cursor.execute('SELECT id FROM task_lists WHERE user_id = ? AND list_name = ?', (user_id, task_list_name))
    task_list_id = cursor.fetchone()
    if task_list_id is None:
        cursor.execute('INSERT INTO task_lists (user_id, list_name, list_type) VALUES (?, ?, ?)',
                       (user_id, task_list_name, task_list_type))
        conn.commit()
        bot.send_message(chat_id, f"{texts['task_list_created_prefix'][get_lang(user_id)]} <b>{task_list_name}</b> {texts['task_list_created_suffix'][get_lang(user_id)]}.", parse_mode='Html')
    else:
        bot.send_message(chat_id, texts['task_list_already_exist'][get_lang(user_id)])


def delete_task_list(user_id, task_list_name):
    cursor.execute('SELECT id FROM task_lists WHERE user_id = ? AND list_name = ?', (user_id, task_list_name))
    task_list_id = cursor.fetchone()

    cursor.execute('DELETE FROM tasks WHERE task_list_id=?', (task_list_id[0],))
    conn.commit()

    cursor.execute('DELETE FROM task_lists WHERE id=?', (task_list_id[0],))
    conn.commit()


def send_task_lists(message, edit=False, current_page=0):
    user_id = message.chat.id
    message_id = message.message_id
    task_lists = get_task_lists(user_id)

    if len(task_lists) == 0:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton(texts['create_list_btn'][get_lang(user_id)], callback_data=f"createList_0"))

        if edit:
            bot.edit_message_text(chat_id=user_id, message_id=message_id, text=texts['no_lists_warn'][get_lang(user_id)], reply_markup=keyboard)
        else:
            bot.send_message(chat_id=user_id, text=texts['no_lists_warn'][get_lang(user_id)], reply_markup=keyboard)
        return

    message = texts['task_lists_title'][get_lang(user_id)]

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    start_index = current_page * items_per_page
    end_index = (current_page + 1) * items_per_page
    for task_list in task_lists[start_index:end_index]:
        keyboard.row(
            types.InlineKeyboardButton(task_list[0], callback_data=f"list_{task_list[0]}"),
            types.InlineKeyboardButton('❌', callback_data=f"deleteList_{task_list[0]}")
        )

    prev_button = types.InlineKeyboardButton(text=texts['previous_btn'][get_lang(user_id)], callback_data=f'prevTaskLists_{current_page}')
    next_button = types.InlineKeyboardButton(text=texts['next_btn'][get_lang(user_id)], callback_data=f'nextTaskLists_{current_page}')

    if current_page > 0:
        keyboard.row(prev_button)
    if end_index < len(task_lists):
        keyboard.row(next_button)

    keyboard.add(types.InlineKeyboardButton(texts['create_list_btn'][get_lang(user_id)], callback_data=f"createList_0"))

    if edit:
        bot.edit_message_text(chat_id=user_id, text=message, message_id=message_id, reply_markup=keyboard)
    else:
        bot.send_message(chat_id=user_id, text=message, reply_markup=keyboard)