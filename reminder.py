import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from telebot import types

from configs import bot, scheduler, texts
from db import cursor, create_connection, conn
from user import get_lang


def get_reminder(user_id, reminder_text, reminder_time):
    cursor.execute("SELECT id FROM reminders WHERE user_id=? AND reminder_text=? AND reminder_date=?",
                   (user_id, reminder_text, reminder_time,))
    reminder = cursor.fetchone()

    return reminder


def set_job_to_reminder(job_id, reminder_id):
    cursor.execute("UPDATE reminders SET job_id = ? WHERE id = ?", (job_id, reminder_id,))
    conn.commit()


def set_reminder(user_id, text, reminder_time):
    add_reminder_to_db(user_id, text, reminder_time)
    reminder = get_reminder(user_id, text, reminder_time)
    job = scheduler.add_job(send_reminder, DateTrigger(run_date=reminder_time), args=[user_id, text, reminder[0]])
    set_job_to_reminder(job.id, reminder[0])


def cancel_reminder(user_id, reminder_id):
    cursor.execute("SELECT job_id FROM reminders WHERE id=?", (reminder_id,))
    reminder = cursor.fetchone()
    job = scheduler.get_job(reminder[0])
    if job and job.args[0] == user_id:
        job.remove()
        delete_reminder_from_db(reminder_id)


def send_reminder(user_id, text, reminder_id):
    message = texts['send_reminder_prefix'][get_lang(user_id)] + " {}".format(text)
    bot.send_message(user_id, message)
    delete_reminder_from_db(reminder_id)


def get_reminders(user_id):
    cursor.execute("SELECT id, user_id, reminder_text, reminder_date FROM reminders WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    reminders = []
    for row in rows:
        reminders.append({
            'id': row[0],
            'text': row[2],
            'reminder_time': row[3],
            # 'status': row[4]
        })

    return reminders


def get_all_reminders():
    cursor.execute("SELECT id, user_id, reminder_text, reminder_date FROM reminders", ())
    rows = cursor.fetchall()
    reminders = []
    for row in rows:
        reminders.append({
            'id': row[0],
            'text': row[2],
            'reminder_time': row[3],
            'user_id': row[1]
            # 'status': row[4]
        })

    return reminders


def add_reminder_to_db(user_id, text, reminder_time):
    cursor.execute("INSERT INTO reminders (user_id, reminder_text, reminder_date) VALUES (?, ?, ?)",
              (user_id, text, reminder_time,))
    conn.commit()


def delete_reminder_from_db(reminder_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
    conn.commit()
    conn.close()


def list_reminders(message):
    chat_id = message.chat.id
    reminders = get_reminders(message.from_user.id)
    user_id = message.from_user.id

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(texts['add_reminder'][get_lang(user_id)], callback_data=f'addReminder_0'))

    if len(reminders) > 0:
        keyboard.add(types.InlineKeyboardButton(texts['cancel_reminder'][get_lang(user_id)], callback_data=f'startCancelReminder_0'))
        message = "Reminders:\n"
        for i, reminder in enumerate(reminders):
            message += f'{i+1}. <b>{reminder["text"]}</b> - <code>{reminder["reminder_time"]}</code>\n'

        bot.send_message(chat_id, message, parse_mode='Html', reply_markup=keyboard)
    else:
        bot.send_message(chat_id, texts['empty_reminders_list'][get_lang(user_id)], reply_markup=keyboard)


def set_reminder_date_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        date_text = f"2023-{message.text}:00"
        date_time = datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
        present = datetime.datetime.now()

        if date_time < present:
            bot.send_message(chat_id, texts['error_past_date'][get_lang(user_id)])
            return
    except ValueError:
        bot.send_message(chat_id, texts['error_date_format'][get_lang(user_id)])
        return

    msg = bot.send_message(chat_id, texts['enter_reminder_text'][get_lang(user_id)])
    bot.register_next_step_handler(msg, set_reminder_text_handler, date_time)


def set_reminder_text_handler(message, date_time):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text

    set_reminder(message.from_user.id, text, date_time)
    bot.send_message(chat_id, f'{texts["reminder"][get_lang(user_id)]} "{text}" {texts["reminder_set_at"][get_lang(user_id)]} {date_time.strftime("%m-%d %H:%M")}')


def set_scheduler():
    reminders = get_all_reminders()

    for reminder in reminders:
        job = scheduler.add_job(send_reminder, DateTrigger(run_date=reminder['reminder_time']), args=[reminder['user_id'], reminder['text'], reminder['id']])
        set_job_to_reminder(job.id, reminder['id'])

