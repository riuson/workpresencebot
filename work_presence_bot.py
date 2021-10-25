#!/usr/bin/env python

# work_presence_bot.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

import sqlite3
# CREATE TABLE records (
#     id          INTEGER  PRIMARY KEY AUTOINCREMENT
#                          UNIQUE
#                          NOT NULL,
#     chat_id     INTEGER  NOT NULL,
#     user_id     INTEGER  NOT NULL,
#     user_name   STRING,
#     time_stamp  DATETIME NOT NULL,
#     record_type INTEGER  NOT NULL,
#     UNIQUE (
#         chat_id,
#         user_id
#     )
#     ON CONFLICT REPLACE
# );

# type of log records
class RecordType:
    CameToWork = 1
    LeftWork = 2
    StayedAtHome = 3


# string value of enum RecordType
record_type_strings = {
    RecordType.LeftWork: 'left work',
    RecordType.CameToWork: 'came to work',
    RecordType.StayedAtHome: 'stayed at home',
}


# function to handle the /start command
def start(update, context):
    first_name = update.message.chat.first_name
    update.message.reply_text(f"Hi {first_name}, nice to meet you!")


# function to handle the /help command
def help(update, context):
    update.message.reply_text("""List of commands:
/start - start bot.
/help - this help.
/menu - call main menu.
/came_to_work - user came to work.
/left_work - user left work.
/stayed_at_home - user stayed at home.""")


# function to handle the /end command
def end(update, context):
    update.message.reply_text('end command received')


# function to handle the /came_to_work command
def came_to_work(update, context):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    update.message.reply_html(
        f'<a href="tg://user?id={user_id}">{user_name}</a> came to work!')
    update_record(
        chat_id=update.message.chat.id,
        user_id=user_id,
        user_name=user_name,
        time_stamp=update.message.date,
        record_type=RecordType.CameToWork)


# function to handle the /left_work command
def left_work(update, context):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    update.message.reply_html(
        f'<a href="tg://user?id={user_id}">{user_name}</a> has left work!')
    update_record(
        chat_id=update.message.chat.id,
        user_id=user_id,
        user_name=user_name,
        time_stamp=update.message.date,
        record_type=RecordType.LeftWork)


# function to handle the /stayed_at_home command
def stayed_at_home(update, context):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    update.message.reply_html(
        f'<a href="tg://user?id={user_id}">{user_name}</a> stayed at home!')
    update_record(
        chat_id=update.message.chat.id,
        user_id=update.message.from_user.id,
        user_name=update.message.from_user.first_name,
        time_stamp=update.message.date,
        record_type=RecordType.StayedAtHome)


# function to handle the /stats command
def stats(update, context):
    msg = get_stats_formatted_for_chat(update.message.chat.id)
    update.message.reply_html(msg)


# function to handle the /menu command
def menu(update, context):
    keyboard = [
        [
            InlineKeyboardButton("Came to work", callback_data=RecordType.CameToWork),
            InlineKeyboardButton("Left work", callback_data=RecordType.LeftWork),
            InlineKeyboardButton("Stayed at home", callback_data=RecordType.StayedAtHome),
        ],
        [InlineKeyboardButton("Stats", callback_data='stats')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


# function to handle errors occurred in the dispatcher
def error(update, context):
    update.message.reply_text('an error occurred')


# function to handle normal text
def text(update, context):
    text_received = update.message.text
    date_received = update.message.date
    chat_id = update.message.chat.id
    # update.message.reply_text(f'did you said "{text_received}" at {date_received} #{id_received} ?')
    update.message.reply_markdown(f'did you said _"{text_received}"_ at *{date_received}* from chat *#{chat_id}* ?')


# function to handle buttons
def button(update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    user_id = query.from_user.id
    user_name = query.from_user.first_name

    #query.edit_message_text(text=f"Selected option: {query.data}")
    if query.data == 'stats':
        query.edit_message_text(text='Stats will be show below.')
        msg = get_stats_formatted_for_chat(query.message.chat.id)
        query.message.reply_html(msg)
    elif query.data.isdigit():
        type_str = record_type_strings[int(query.data)]
        update_record(
            chat_id=query.message.chat.id,
            user_id=user_id,
            user_name=user_name,
            time_stamp=query.message.date,
            record_type=int(query.data))
        msg = f'{user_name}, you {type_str}'
        query.edit_message_text(text=msg)


# get records for chat
def get_records(chat_id):
    connection = sqlite3.connect('presence_bot_records.sqlite3', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute('select user_id, user_name, time_stamp, record_type from records where chat_id = ? order by time_stamp desc', [chat_id])
    table = cursor.fetchall()
    connection.close()
    return table


# update record in table
def update_record(chat_id, user_id, user_name, time_stamp, record_type):
    connection = sqlite3.connect('presence_bot_records.sqlite3', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(
        'insert into records (chat_id, user_id, user_name, time_stamp, record_type) values (?, ?, ?, ?, ?)',
        [chat_id, user_id, user_name, time_stamp, record_type])
    connection.commit()
    connection.close()


# format log record
def format_record(record):
    # 0 - user_id, 1 - user_name, 2 - time_stamp, 3 - record_type
    msg = f'<a href="tg://user?id={record[0]}">{record[1]}</a> ';

    #match record[3]:
    #    case RecordType.CameToWork:
    #        msg += 'came'
    #    case RecordType.LeftWork:
    #        msg += 'left'
    #    case RecordType.StayedAtHome:
    #        msg += 'stayed at home'
    msg += record_type_strings[record[3]]

    msg += f'\n{record[2]}'
    return msg


# get stats for chat in formatted form
def get_stats_formatted_for_chat(chat_id):
    records = get_records(chat_id)
    work = ""
    home = ""
    for record in records:
        if record[3] == RecordType.CameToWork:
            work += format_record(record) + "\n"
        else:
            home += format_record(record) + "\n"
    msg = ""
    if work != "":
        msg = "<b>At work:</b>\n" + work
    if home != "":
        if work != "":
            msg += "\n"
        msg += "<b>At home:</b>\n" + home
    return msg


def main():
    TOKEN = "<token>"

    # create the updater, that will automatically create also a dispatcher and a queue to 
    # make them dialoge
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # add handlers for start and help commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("came_to_work", came_to_work))
    dispatcher.add_handler(CommandHandler("left_work", left_work))
    dispatcher.add_handler(CommandHandler("stayed_at_home", stayed_at_home))
    dispatcher.add_handler(CommandHandler("stats", stats))
    dispatcher.add_handler(CommandHandler("menu", menu))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CallbackQueryHandler(button))

    # add an handler for errors
    dispatcher.add_error_handler(error)

    # start bot
    updater.start_polling()

    # run the bot until Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
