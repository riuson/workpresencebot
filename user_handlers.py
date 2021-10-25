#!/usr/bin/env python

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import CallbackContext  # , MessageHandler, Filters, Updater, CommandHandler, CallbackQueryHandler,
from emoji import emojize
import data_storage as storage


# emoji:  https://www.webfx.com/tools/emoji-cheat-sheet/


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
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    # update.message.reply_text(f"Hi {first_name}, nice to meet you!")
    update.message.chat.send_message(
        f'Hello, <a href="tg://user?id={user_id}">{first_name}</a>',
        parse_mode=ParseMode.HTML)


# function to handle the /help command
def help(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    update.message.chat.send_message(
        f'''<a href="tg://user?id={user_id}">{first_name}</a>, list of commands:
/start - Start bot.
/help - Display help message.
/menu - Display main menu.
/stats - Display stats of users.
/stay - User stayed at home.
/came - User came to work.
/left - User left work.''',
        parse_mode=ParseMode.HTML)


# commands for @BotFather:
# stay - User stayed at home.
# came - User came to work.
# left - User left work.
# start - Start bot.
# help - Display help message.
# menu - Display main menu.
# stats - Display stats of users

# function to handle the /stay command
def stay(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    # update.message.reply_text(f"{first_name} stayed at home!")
    # update.message.reply_html(
    #    f'<a href="tg://user?id={user_id}">{user_name}</a> has left work!')
    storage.update_record(
        chat_id=update.message.chat.id,
        user_id=user_id,
        user_name=first_name,
        time_stamp=update.message.date,
        record_type=RecordType.StayedAtHome)
    update.message.chat.send_message(
        emojize(f'<a href="tg://user?id={user_id}">{first_name}</a> :house: :thumbsup:', use_aliases=True),
        parse_mode=ParseMode.HTML)


# function to handle the /came command
def came(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    # update.message.reply_text(f"{first_name} came to work!")
    storage.update_record(
        chat_id=update.message.chat.id,
        user_id=user_id,
        user_name=first_name,
        time_stamp=update.message.date,
        record_type=RecordType.CameToWork)
    update.message.chat.send_message(
        emojize(f'<a href="tg://user?id={user_id}">{first_name}</a> :office: :thumbsup:', use_aliases=True),
        parse_mode=ParseMode.HTML)


# function to handle the /left command
def left(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    # update.message.reply_text(f"{first_name} has left work home!")
    storage.update_record(
        chat_id=update.message.chat.id,
        user_id=user_id,
        user_name=first_name,
        time_stamp=update.message.date,
        record_type=RecordType.LeftWork)
    update.message.chat.send_message(
        emojize(f'<a href="tg://user?id={user_id}">{first_name}</a> :house: :thumbsup:', use_aliases=True),
        parse_mode=ParseMode.HTML)


# function to handle the /stats command
def stats(update: Update, context: CallbackContext) -> None:
    msg = get_stats_formatted_for_chat(update.message.chat.id)
    # update.message.reply_html(msg)
    update.message.chat.send_message(
        emojize(msg, use_aliases=True),
        parse_mode=ParseMode.HTML)


# function to handle the /menu command
def menu(update: Update, context: CallbackContext) -> None:
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
def button(update: Update, context: CallbackContext) -> None:
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


# echo test
def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('sjdhahdjk')


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

    msg += f'\n<i>{record[2]}</i>'
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
        msg = "<b>At work</b> :office:\n" + work
    if home != "":
        if work != "":
            msg += "\n"
        msg += "<b>At home</b> :house:\n" + home
    return msg
