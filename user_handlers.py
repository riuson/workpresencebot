#!/usr/bin/env python

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
import data_storage as storage


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
def start(update, context) -> None:
    first_name = update.message.chat.first_name
    update.message.reply_text(f"Hi {first_name}, nice to meet you!")


# function to handle the /help command
def help(update, context) -> None:
    update.message.reply_text("""List of commands:
/start - start bot.
/help - this help.
/menu - call main menu.
/came_to_work - user came to work.
/left_work - user left work.
/stayed_at_home - user stayed at home.""")


# function to handle the /stats command
def stats(update, context) -> None:
    msg = get_stats_formatted_for_chat(update.message.chat.id)
    update.message.reply_html(msg)


# function to handle the /menu command
def menu(update, context) -> None:
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


# function to handle buttons
def button(update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    user_id = query.from_user.id
    user_name = query.from_user.first_name

    # query.edit_message_text(text=f"Selected option: {query.data}")
    if query.data == 'stats':
        query.edit_message_text(text='Stats will be show below.')
        msg = get_stats_formatted_for_chat(query.message.chat.id)
        query.message.reply_html(msg)
    elif query.data.isdigit():
        type_str = record_type_strings[int(query.data)]
        storage.update_record(
            chat_id=query.message.chat.id,
            user_id=user_id,
            user_name=user_name,
            time_stamp=query.message.date,
            record_type=int(query.data))
        msg = f'{user_name}, you {type_str}'
        query.edit_message_text(text=msg)


# format log record
def format_record(record) -> str:
    # 0 - user_id, 1 - user_name, 2 - time_stamp, 3 - record_type
    msg = f'<a href="tg://user?id={record[0]}">{record[1]}</a> ';

    # match record[3]:
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
def get_stats_formatted_for_chat(chat_id) -> str:
    records = storage.get_records(chat_id)
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
