import config
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from random import randint
import sqlite3

bot = telebot.TeleBot(config.API_TOKEN)


def senf_info(bot, message, row):

    info = f"""
📍Title of movie:   {row[2]}
📍Year:                   {row[3]}
📍Genres:              {row[4]}
📍Rating IMDB:      {row[5]}


🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻
{row[6]}
"""
    bot.send_photo(message.chat.id, row[1])
    bot.send_message(message.chat.id, info,
                     reply_markup=add_to_favorite(row[0]))


def add_to_favorite(id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(
        "Добавить фильм в избранное 🌟", callback_data=f'favorite_{id}'))
    return markup


def main_markup():
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('/random'))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("favorite"):
        id = call.data[call.data.find("_")+1:]
        parts = call.data.split("_")
        user_id = call.from_user.id
        movie_id = int(parts[1])
        con = sqlite3.connect("movie_database.db")  # подключене к бд
    with con:
        cur = con.cursor()  # создание курсора
        cur.execute("INSERT INTO favorites_movie (user_id, movie_id) VALUES (?, ?)",
                    (user_id, movie_id))  # взаимодействие с бд
        cur.close()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """Hello! You're welcome to the best Movie-Chat-Bot🎥!
Here you can find 1000 movies 🔥
Click /random to get random movie
Or write the title of movie and I will try to find it! 🎬 """, reply_markup=main_markup()
                     )


@bot.message_handler(commands=['random'])
def random_movie(message):
    con = sqlite3.connect("movie_database.db")
    with con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM movies ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchall()[0]
        cur.close()
    senf_info(bot, message, row)


@bot.message_handler(commands=['favorites'])
def favorite_handler(message):
    user_id = message.from_user.id
    con = sqlite3.connect("movie_database.db")

    with con:
        cur = con.cursor()
        cur1 = con.cursor()
        movies = []
        for row in cur.execute("select movie_id from favorites_movie where user_id = ?", (user_id,)):
            cur1.execute("select title from movies where id = ?", (row[0],))
            title = cur1.fetchone()
            movies.append(title[0])
        cur1.close()
        cur.close()

    movies = '\
    '.join(movies)

    bot.send_message(message.chat.id, movies)


@bot.message_handler(func=lambda message: True)
def echo_message(message):

    con = sqlite3.connect("movie_database.db")
    with con:
        cur = con.cursor()
        cur.execute(
            f"select * from movies where LOWER(title) = '{message.text.lower()}'")
        row = cur.fetchall()
        if row:
            row = row[0]
            bot.send_message(message.chat.id, "Of course! I know this movie😌")
            senf_info(bot, message, row)
        else:
            bot.send_message(message.chat.id, "I don't know this movie ")

        cur.close()


bot.infinity_polling()
