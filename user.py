from db import cursor, conn


def get_lang(user_id):
    cursor.execute('SELECT lang FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    lang = user[0]
    if lang == 'ru' or lang == 'ua' or lang == 'kz':
        return 'ru'
    else:
        return 'en'


def add_user(user_id, username, lang):
    cursor.execute(
        "INSERT INTO users (user_id, lang, username, meta) VALUES (?, ?, ?, '')",
        (user_id, lang, username,))
    conn.commit()
