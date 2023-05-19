# Создаем экземпляр бота
import logging
import threading

import telebot
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = telebot.logger
bot = telebot.TeleBot('5998142859:AAFkWNz7dZmqF6729oWlRdJSLTkaXi_I6-8')
telebot.logger.setLevel(logging.INFO) # Outputs debug messages to console.


texts = {
    'add_task_btn': {
        'ru': 'Добавить цель',
        'en': 'Add task'
    },
    'reminders_btn': {
        'ru': 'Напоминания',
        'en': 'Reminders'
    },
    'create_list_btn': {
        'ru': 'Создать список',
        'en': 'Create List'
    },
    'lists_btn': {
        'ru': 'Списки',
        'en': 'Lists'
    },
    'greeting': {
        'ru': 'Привет! Я - GetBetter-бот 🤖\n\n'
              '🏆 Миссия GetBetter – заменить планировщик дел и времени, '
              'трекер привычек, напоминания, заметки, ежедневник, '
              'и помочь сохранить всю важную информацию в удобном, полезном приложении.\n\n'
              'Мой функционал активно развивается, в дальнейшем я буду сообщать тебе о появлении новых возможностей 😉\n\n'
              'Если у тебя появятся какие-то вопросы, пиши моему разработчику, '
              'он с удовольствием тебе поможет - @velkonost',
        'en': 'Hello! I\'m GetBetter-bot 🤖\n\n'
              '🏆 GetBetter\'s mission is to replace the to-do and time planner, '
              'habit tracker, reminders, notes, diary,'
              'and help keep all your important information in a handy, useful app.\n\n'
              'My functionality is actively developing, in the future '
              'I will inform you about the appearance of new features 😉\n\n'
              'If you have any questions, write to my developer, '
              'he will help you with pleasure - @velkonost',
    },
    'help_btn': {
        'ru': 'Помощь',
        'en': 'Help'
    },
    'help': {
        'ru': '🎯 Хотите самосовершенствоваться?\n'
              '🥇 Хотите продвинуться по карьерной лестнице?\n'
              '👥 Хотите проводить больше времени с семьей?\n'
              '🙌 Хотите поехать в место своей мечты?\n'
              '🗂 Хотите оставить наследство?\n\n'
              '📕 С этими задачами не справится обычный ежедневник.\n'
              '📚 А GetBetter поможет уделить время здоровью, удовольствиям и самореализации.\n'
              '💛 Целевой трекер & Дневник событий помогут вам отслеживать ваши успехи. '
              'В GetBetter ты увидишь свой прогресс и найдешь точки роста!\n\n'
              'Задать вопрос, предложить идею, сообщить об ошибке - @velkonost\n'
              'Группа с новостями - t.me/getbetterandroidapp',
        'en': '🎯 Do you want to improve yourself?\n'
              '🥇 Do you want to move up the career ladder?\n'
              '👥 Do you want to spend more time with your family?\n'
              '🙌 Do you want to go to the place of your dreams?\n'
              '🗂 Do you want to leave a legacy?\n\n📕'
              ' A default diary will not cope with these tasks.\n'
              '📚 And GetBetter will help you devote time to health, pleasure and self-realization.\n'
              '💛 Target Tracker & Event Diary will help you keep track of your progress. '
              'In GetBetter you will see your progress and find growth points!\n\n'
              'Ask a question, suggest an idea, report a bug - @velkonost\n'
              'Newsgroup - t.me/getbetterandroidapp',
    },
    'no_lists_warn': {
        'ru': 'У вас пока нет созданных списков задач',
        'en': 'You don\'t have any task lists created yet'
    },
    'task_lists_title': {
        'ru': 'Списки задач:\n',
        'en': 'Task lists:\n'
    },
    'previous_btn': {
        'ru': 'Назад',
        'en': 'Previous'
    },
    'next_btn': {
        'ru': 'Далее',
        'en': 'Next'
    },
    'list_selected_prefix': {
        'ru': 'Выбран лист',
        'en': 'Selected list'
    },
    'no_tasks_in_list_prefix': {
        'ru': 'У вас пока нет задач в списке',
        'en': 'You don\'t have any tasks in the list'
    },
    'tasks_title': {
        'ru': 'Задачи:\n',
        'en': 'Tasks:\n'
    },
    'enter_list_name': {
        'ru': 'Введите название списка задач:',
        'en': 'Enter the name of the task list:'
    },
    'no': {
        'ru': 'Нет',
        'en': 'No'
    },
    'yes': {
        'ru': 'Да',
        'en': 'Yes'
    },
    'ask_delete_list_prefix': {
        'ru': 'Точно удалить список',
        'en': 'Sure delete list'
    },
    'list_deleted_prefix': {
        'ru': 'Список',
        'en': 'List'
    },
    'list_deleted_suffix': {
        'ru': 'удален!',
        'en': 'deleted!'
    },
    'enter_task_prefix': {
        'ru': 'Введите задачу для списка',
        'en': 'Enter task for list'
    },
    'cancel_status': {
        'ru': 'Отменить выполнение',
        'en': 'Cancel execution'
    },
    'done_status': {
        'ru': 'Выполнить',
        'en': 'Done'
    },
    'delete': {
        'ru': 'Удалить',
        'en': 'Delete'
    },
    'ask_delete_task': {
        'ru': 'Точно удалить?',
        'en': 'Delete task?'
    },
    'task_deleted': {
        'ru': 'Запись удалена!',
        'en': 'Task deleted!'
    },
    'select_reminder_for_cancel': {
        'ru': 'Выберите напоминание для отмены',
        'en': 'Select a reminder to cancel'
    },
    'reminder_canceled': {
        'ru': 'Напоминание отменено!',
        'en': 'Reminder canceled!'
    },
    'add_reminder': {
        'ru': 'Добавить напоминание',
        'en': 'Add reminder'
    },
    'cancel_reminder': {
        'ru': 'Отменить напоминание',
        'en': 'Cancel reminder'
    },
    'reminders_title': {
        'ru': 'Напоминания:\n',
        'en': 'Reminders:\n'
    },
    'empty_reminders_list': {
        'ru': 'Список напоминаний пуст',
        'en': 'Reminder\'s list is empty'
    },
    'enter_reminder_time': {
        'ru': 'Введите дату и время в формате mm-dd HH:MM',
        'en': 'Enter the date and time in the format mm-dd HH:MM'
    },
    'error_past_date': {
        'ru': 'Необходимо указать дату в будущем',
        'en': 'You must specify a date in the future'
    },
    'error_date_format': {
        'ru': 'Неправильный формат даты и времени. Введите в формате mm-dd HH:MM',
        'en': 'Wrong date and time format. Enter in format mm-dd HH:MM'
    },
    'enter_reminder_text': {
        'ru': 'Введите текст напоминания',
        'en': 'Enter reminder text'
    },
    'reminder': {
        'ru': 'Напоминание',
        'en': 'Reminder'
    },
    'reminder_set_at': {
        'ru': 'установлено на',
        'en': 'set on'
    },
    'send_reminder_prefix': {
        'ru': 'Напоминание:',
        'en': 'Reminder:'
    },
    'select_list_for_create_task': {
        'ru': 'Выберите список, в котором создать задачу:\n',
        'en': 'Select the list for create the task:\n'
    },
    'task_added_in_list': {
        'ru': 'Задача добавлена в список',
        'en': 'Task added in list'
    },
    'status': {
        'ru': 'Статус',
        'en': 'Status'
    },
    'task_list_created_prefix': {
        'ru': 'Список задач',
        'en': 'Task list'
    },
    'task_list_created_suffix': {
        'ru': 'создан',
        'en': 'created'
    },
    'task_list_already_exist': {
        'ru': 'Список задач с таким названием уже существует.',
        'en': 'A task list with the same name already exists.'
    }


}

db_name = 'getbetter.db'
items_per_page = 5

# Define the lock globally
lock = threading.Lock()

# Создание планировщика для управления напоминаниями
scheduler = BackgroundScheduler(timezone='UTC')
scheduler.start()