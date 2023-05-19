import logging
import os
import sys
from requests import ReadTimeout
from telebot import types
from callback import list_callback, create_list_callback, prev_tasks_callback, next_tasks_callback, \
    delete_list_callback, task_callback, task_cancel_status_callback, task_done_status_callback, \
    task_delete_callback, task_delete_yes_callback, task_delete_no_callback, start_cancel_reminder_callback, \
    cancel_reminder_callback
from configs import texts, bot
from reminder import list_reminders, set_scheduler, set_reminder_date_handler
from tasks import add_task_step3, add_task
from tasks_list import delete_task_list, send_task_lists
from user import get_lang, add_user


@bot.message_handler(commands=["start"])
def send_welcome(message, res=False):
    logging.info(f"Received /start command from user {message.chat.id} (@{message.from_user.username}): {message.text}")

    add_user(message.from_user.id, message.from_user.username, message.from_user.language_code)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    help_btn = types.KeyboardButton(texts['help_btn'][get_lang(message.from_user.id)])
    add_task_btn = types.KeyboardButton(texts['add_task_btn'][get_lang(message.from_user.id)])
    reminders_btn = types.KeyboardButton(texts['reminders_btn'][get_lang(message.from_user.id)])
    lists_btn = types.KeyboardButton(texts['lists_btn'][get_lang(message.from_user.id)])

    markup.row(help_btn, add_task_btn)
    markup.row(reminders_btn, lists_btn)

    bot.send_message(message.chat.id, texts['greeting'][get_lang(message.from_user.id)], reply_markup=markup)


def send_help(message):
    bot.reply_to(message, texts['help'][get_lang(message.from_user.id)])


# @bot.callback_query_handler(func=lambda call: call.data.startswith('delete_list'))
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    callback_type = call.data.split("_")[0]
    callback_data = call.data.split("_")[1]
    user_id = call.from_user.id
    message_id = call.message.id

    if callback_type == 'list':
        list_callback(call.id, callback_data, user_id, message_id)
    elif callback_type == 'createList':
        create_list_callback(user_id, message_id)
    elif callback_type == 'prevTasks':
        prev_tasks_callback(callback_data, call.data.split("_")[2], user_id, message_id)
    elif callback_type == 'nextTasks':
        next_tasks_callback(callback_data, call.data.split("_")[2], user_id, message_id)
    elif callback_type == 'deleteList':
        delete_list_callback(callback_data, user_id, message_id)
    elif callback_type == 'listDeleteNo':
        send_task_lists(call.message, edit=True)
    elif callback_type == 'listDeleteYes':
        delete_task_list(call.from_user.id, callback_data)
        bot.answer_callback_query(call.id, f"{texts['list_deleted_prefix'][get_lang(call.from_user.id)]} {callback_data} {texts['list_deleted_suffix'][get_lang(call.from_user.id)]}")
        send_task_lists(call.message, edit=True)
    elif callback_type == 'listToAddTask':
        message = bot.edit_message_text(chat_id=user_id, message_id=message_id, text=f'{texts["enter_task_prefix"][get_lang(call.from_user.id)]} <b>"{callback_data}"</b>:', parse_mode='Html', reply_markup=None)
        bot.register_next_step_handler(message, add_task_step3, callback_data)
    elif callback_type == 'task':
        task_callback(callback_data, user_id, message_id)
    elif callback_type == 'taskCancelStatus':
        task_cancel_status_callback(callback_data, user_id, message_id)
    elif callback_type == 'taskDoneStatus':
        task_done_status_callback(callback_data, user_id, message_id)
    elif callback_type == 'taskDelete':
        task_delete_callback(call.message.text, callback_data, user_id, message_id)
    elif callback_type == 'taskDeleteYes':
        task_delete_yes_callback(call.id, callback_data, user_id, message_id)
    elif callback_type == 'taskDeleteNo':
        task_delete_no_callback(callback_data, user_id, message_id)
    elif callback_type == 'prevTaskLists':
        send_task_lists(call.message, edit=True, current_page=int(callback_data) - 1)
    elif callback_type == 'nextTaskLists':
        send_task_lists(call.message, edit=True, current_page=int(callback_data) + 1)
    elif callback_type == 'startCancelReminder':
        start_cancel_reminder_callback(user_id, message_id)
    elif callback_type == 'cancelReminder':
        cancel_reminder_callback(call.id, callback_data, user_id, message_id)
    elif callback_type == 'addReminder':
        msg = bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text=texts['enter_reminder_time'][get_lang(call.from_user.id)])
        bot.register_next_step_handler(msg, set_reminder_date_handler)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    logging.info(f"Received message from user {message.chat.id} (@{message.from_user.username}): {message.text}")
    message_text = message.text.strip().lower()
    user_id = message.from_user.id

    if message_text == texts['help_btn'][get_lang(user_id)].lower():
        send_help(message)
    elif message_text == texts['add_task_btn'][get_lang(user_id)].lower():
        add_task(message)
    elif message_text == texts['lists_btn'][get_lang(user_id)].lower():
        send_task_lists(message)
    elif message_text == texts['reminders_btn'][get_lang(user_id)].lower():
        list_reminders(message)


try:
    exec(open("db.py").read())

    set_scheduler()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
except (ConnectionError, ReadTimeout) as e:
    sys.stdout.flush()
    os.execv(sys.argv[0], sys.argv)
else:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)