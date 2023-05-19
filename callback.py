from telebot import types

from configs import bot, texts, items_per_page
from reminder import get_reminders, cancel_reminder
from tasks import get_tasks, get_task, update_task_status, delete_task
from tasks_list import add_task_list
from user import get_lang


def list_callback(call_id, callback_data, user_id, message_id):
    bot.answer_callback_query(call_id, f"{texts['list_selected_prefix'][get_lang(user_id)]} {callback_data}")
    tasks = get_tasks(user_id, callback_data)

    if len(tasks) == 0:
        bot.send_message(chat_id=user_id,
                         text=f'{texts["no_tasks_in_list_prefix"][get_lang(user_id)]} {callback_data}')
        return

    message = texts['tasks_title'][get_lang(user_id)]
    keyboard = types.InlineKeyboardMarkup()
    current_page = 0
    start_index = current_page * items_per_page
    end_index = (current_page + 1) * items_per_page
    for task in tasks[start_index:end_index]:
        keyboard.add(types.InlineKeyboardButton(task[1], callback_data=f"task_{task[0]}"))

    prev_button = types.InlineKeyboardButton(text=texts['previous_btn'][get_lang(user_id)],
                                                     callback_data=f'prevTasks_{current_page}_{callback_data}')
    next_button = types.InlineKeyboardButton(text=texts['next_btn'][get_lang(user_id)],
                                                     callback_data=f'nextTasks_{current_page}_{callback_data}')
    if current_page > 0:
        keyboard.row(prev_button)
    if end_index < len(tasks):
        keyboard.row(next_button)
    bot.edit_message_text(chat_id=user_id, message_id=message_id, text=message, reply_markup=keyboard)


def create_list_callback(user_id, message_id):
    msg = bot.edit_message_text(chat_id=user_id, message_id=message_id,
                                text=texts['enter_list_name'][get_lang(user_id)])
    bot.register_next_step_handler(msg, add_task_list)


def prev_tasks_callback(callback_data, callback_data_second, user_id, message_id):
    tasks = get_tasks(user_id, callback_data_second)

    message = texts['tasks_title'][get_lang(user_id)]
    keyboard = types.InlineKeyboardMarkup()
    current_page = int(callback_data) - 1
    start_index = current_page * items_per_page
    end_index = (current_page + 1) * items_per_page
    for task in tasks[start_index:end_index]:
        keyboard.add(types.InlineKeyboardButton(task[1], callback_data=f"task_{task[0]}"))

    prev_button = types.InlineKeyboardButton(text=texts['previous_btn'][get_lang(user_id)],
                                                     callback_data=f'prevTasks_{current_page}_{callback_data_second}')
    next_button = types.InlineKeyboardButton(text=texts['next_btn'][get_lang(user_id)],
                                                     callback_data=f'nextTasks_{current_page}_{callback_data_second}')

    if current_page > 0:
        keyboard.row(prev_button)
    if end_index < len(tasks):
        keyboard.row(next_button)

    bot.edit_message_text(chat_id=user_id, message_id=message_id, text=message, reply_markup=keyboard)


def next_tasks_callback(callback_data, callback_data_second, user_id, message_id):
    tasks = get_tasks(user_id, callback_data_second)

    message = texts['tasks_title'][get_lang(user_id)]
    keyboard = types.InlineKeyboardMarkup()
    current_page = int(callback_data) + 1
    start_index = current_page * items_per_page
    end_index = (current_page + 1) * items_per_page
    for task in tasks[start_index:end_index]:
        keyboard.add(types.InlineKeyboardButton(task[1], callback_data=f"task_{task[0]}"))

    prev_button = types.InlineKeyboardButton(text=texts['previous_btn'][get_lang(user_id)],
                                                     callback_data=f'prevTasks_{current_page}_{callback_data_second}')
    next_button = types.InlineKeyboardButton(text=texts['next_btn'][get_lang(user_id)],
                                                     callback_data=f'nextTasks_{current_page}_{callback_data_second}')

    if current_page > 0:
        keyboard.row(prev_button)
    if end_index < len(tasks):
        keyboard.row(next_button)
    bot.edit_message_text(chat_id=user_id, message_id=message_id, text=message, reply_markup=keyboard)


def delete_list_callback(callback_data, user_id, message_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(texts['no'][get_lang(user_id)],
                                            callback_data=f"listDeleteNo_{callback_data}"))
    keyboard.add(types.InlineKeyboardButton(texts['yes'][get_lang(user_id)],
                                            callback_data=f"listDeleteYes_{callback_data}"))
    bot.edit_message_text(chat_id=user_id, message_id=message_id,
                          text=f"<b>{texts['ask_delete_list_prefix'][get_lang(user_id)]} {callback_data}?</b>",
                          reply_markup=keyboard, parse_mode='Html')


def task_callback(callback_data, user_id, message_id):
    task = get_task(callback_data, user_id)
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    if task[1] == 1:
        keyboard.add(types.InlineKeyboardButton(texts['cancel_status'][get_lang(user_id)],
                                                callback_data=f"taskCancelStatus_{callback_data}"))
    else:
        keyboard.add(types.InlineKeyboardButton(texts['done_status'][get_lang(user_id)],
                                                callback_data=f"taskDoneStatus_{callback_data}"))

    keyboard.add(types.InlineKeyboardButton(texts['delete'][get_lang(user_id)],
                                            callback_data=f"taskDelete_{callback_data}"))
    bot.edit_message_text(chat_id=user_id, message_id=message_id, text=task[0], reply_markup=keyboard)


def task_cancel_status_callback(callback_data, user_id, message_id):
    update_task_status(callback_data, 0)
    task = get_task(callback_data, user_id)
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    if task[1] == 1:
        keyboard.add(
            types.InlineKeyboardButton(texts['cancel_status'][get_lang(user_id)],
                                       callback_data=f"taskCancelStatus_{callback_data}"))
    else:
        keyboard.add(types.InlineKeyboardButton(texts['done_status'][get_lang(user_id)],
                                                callback_data=f"taskDoneStatus_{callback_data}"))

    keyboard.add(types.InlineKeyboardButton(texts['delete'][get_lang(user_id)],
                                            callback_data=f"taskDelete_{callback_data}"))
    bot.edit_message_text(chat_id=user_id, message_id=message_id, text=task[0], reply_markup=keyboard)


def task_done_status_callback(callback_data, user_id, message_id):
    update_task_status(callback_data, 1)
    task = get_task(callback_data, user_id)
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    if task[1] == 1:
        keyboard.add(
            types.InlineKeyboardButton(texts['cancel_status'][get_lang(user_id)],
                                       callback_data=f"taskCancelStatus_{callback_data}"))
    else:
        keyboard.add(types.InlineKeyboardButton(texts['done_status'][get_lang(user_id)],
                                                callback_data=f"taskDoneStatus_{callback_data}"))

    keyboard.add(types.InlineKeyboardButton(texts['delete'][get_lang(user_id)],
                                            callback_data=f"taskDelete_{callback_data}"))
    bot.edit_message_text(chat_id=user_id, message_id=message_id, text=task[0], reply_markup=keyboard)


def task_delete_callback(message_text, callback_data, user_id, message_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(texts['no'][get_lang(user_id)],
                                            callback_data=f"taskDeleteNo_{callback_data}"))
    keyboard.add(types.InlineKeyboardButton(texts['yes'][get_lang(user_id)],
                                            callback_data=f"taskDeleteYes_{callback_data}"))
    bot.edit_message_text(chat_id=user_id, message_id=message_id,
                          text=f"<b>{texts['ask_delete_task'][get_lang(user_id)]}</b>\n\n{message_text}",
                          reply_markup=keyboard, parse_mode='Html')


def task_delete_yes_callback(call_id, callback_data, user_id, message_id):
    bot.answer_callback_query(call_id, f"{texts['task_deleted'][get_lang(user_id)]}")
    delete_task(callback_data)
    bot.edit_message_text(chat_id=user_id, message_id=message_id,
                          text=texts['task_deleted'][get_lang(user_id)], reply_markup=None)


def task_delete_no_callback(callback_data, user_id, message_id):
    task = get_task(callback_data, user_id)
    keyboard = types.InlineKeyboardMarkup()
    if task[1] == 1:
        keyboard.add(types.InlineKeyboardButton(texts['cancel_status'][get_lang(user_id)],
                                                callback_data=f"taskCancelStatus_{callback_data}"))
    else:
        keyboard.add(types.InlineKeyboardButton(texts['done_status'][get_lang(user_id)],
                                                callback_data=f"taskDoneStatus_{callback_data}"))
    keyboard.add(types.InlineKeyboardButton(texts['delete'][get_lang(user_id)],
                                            callback_data=f"taskDelete_{callback_data}"))
    bot.edit_message_text(chat_id=user_id, message_id=message_id, text=task[0],
                          reply_markup=keyboard)


def start_cancel_reminder_callback(user_id, message_id):
    reminders = get_reminders(user_id)

    keyboard = types.InlineKeyboardMarkup()
    for i, reminder in enumerate(reminders):
        button = types.InlineKeyboardButton(f'{i + 1}. {reminder["text"]}',
                                            callback_data=f'cancelReminder_{reminder["id"]}')
        keyboard.add(button)
    bot.edit_message_text(chat_id=user_id, message_id=message_id,
                          text=texts['select_reminder_for_cancel'][get_lang(user_id)], reply_markup=keyboard)


def cancel_reminder_callback(call_id, callback_data, user_id, message_id):
    cancel_reminder(user_id, callback_data)
    bot.answer_callback_query(call_id, texts['reminder_canceled'][get_lang(user_id)])

    reminders = get_reminders(user_id)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(texts['add_reminder'][get_lang(user_id)], callback_data=f'addReminder_0'))

    if len(reminders) > 0:
        keyboard.add(types.InlineKeyboardButton(texts['cancel_reminder'][get_lang(user_id)],
                                                callback_data=f'startCancelReminder_0'))
        message = texts['reminders_title'][get_lang(user_id)]
        for i, reminder in enumerate(reminders):
            message += f'{i + 1}. <b>{reminder["text"]}</b> - <code>{reminder["reminder_time"]}</code>\n'

        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=message, parse_mode='Html',
                              reply_markup=keyboard)
    else:
        bot.edit_message_text(chat_id=user_id, message_id=message_id,
                              text=texts['empty_reminders_list'][get_lang(user_id)], reply_markup=keyboard)