import telebot, time, config
import sqlite3 as sq
from telebot import types
from main import *

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()

    key_weather = types.InlineKeyboardButton(text='Погода', callback_data='weather')
    keyboard.add(key_weather)

    key_exchanges = types.InlineKeyboardButton(text='Курс валют', callback_data='exchanges')
    keyboard.add(key_exchanges)

    answer = 'Привет! Что хочешь узнать: погоду в Новотроицке или курс валют(USD, EURO, KZT, CNY)\n' \
             'Или же информацию о себе? :) (Напиши /info)'

    bot.send_message(message.from_user.id, text=answer, reply_markup=keyboard)

    #                  creating a database and adding user information
    db = sq.connect('users.db', timeout=10)
    cur = db.cursor()

    cur.execute('''
                    CREATE TABLE IF NOT EXISTS Users
                    (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    users_id INTEGER NOT NULL UNIQUE,
                    username TEXT,
                    nickname TEXT
                    )
        ''')
    ###################################################################################################################
    array = list()

    user_id = message.from_user.id
    if message.from_user.username is None:
        user_username = 'None'
    else:
        user_username = f'@{message.from_user.username}'
    user_first_name = message.from_user.first_name
    user_last_name = message.from_user.last_name
    user_nickname = f'{user_first_name} {user_last_name}'

    array.append(user_id), array.append(user_username), array.append(user_nickname)

    try:
        sql_insert = '''INSERT INTO Users (users_id, username, nickname) VALUES (?, ?, ?)'''
        tuple1 = (array[0], array[1], array[2])
        print(tuple1)

        db.execute(sql_insert, tuple1)

        db.commit()

        db.close()

    except sq.IntegrityError as Error:  # обработка ошибки, если у нас не уникальный user_id
        id_ = cur.execute('SELECT id FROM Users WHERE users_id =:users_id', {'users_id': array[0]}).fetchone()

        print(id_[0])

        cur.execute('UPDATE Users set username =:username, nickname =:nickname WHERE id =:id',
                    {'id': id_[0], 'username': array[1], 'nickname': array[2]})

        print('UPDATE DATA IN THE DB', array)

        db.commit()

        db.close()


@bot.message_handler(commands=['info'])
def give_information_about_user(message):
    user_id = message.from_user.id
    user_username = '@' + message.from_user.username
    user_first_name = message.from_user.first_name
    user_last_name = message.from_user.last_name
    user_nickname = f'{user_first_name} {user_last_name}'
    user = f'id: {user_id}, username: {user_username}, name: {user_nickname}'

    bot.send_message(message.from_user.id, user)

    # bot.register_next_step_handler(message, create_db)


@bot.message_handler(commands=['help'])
def give_help(message):
    bot.send_message(message.from_user.id, 'Напиши /start')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if __name__ == '__main__':
        pars.parsing_exchange()
        pars.parsing_weather()
        pars.save_in_json()

    with open('Parse_exchange_and_weather_Ntsk.json') as file:
        read_json = json.load(file)

    result = ''

    if call.data == 'weather':
        del read_json['exchange']
        for elem in read_json:
            result += f'{elem}: {read_json[elem]}'
            result += '\n'
        bot.send_message(call.message.chat.id, result)

    elif call.data == 'exchanges':
        exchanges = '-'.join(read_json['exchange']).replace(' ', ': ').split('-')
        for elem in exchanges:
            result += elem
            result += '\n'
        bot.send_message(call.message.chat.id, result)


@bot.message_handler(content_types=['text'])
def create_db(message):
    bot.send_message(message.from_user.id, 'Я тебя не понимаю. Напиши /help')


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(3)
            print(e)
