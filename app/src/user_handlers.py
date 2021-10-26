#!/usr/bin/env python

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import CallbackContext  # , MessageHandler, Filters, Updater, CommandHandler, CallbackQueryHandler,
from emoji import emojize
import data_storage as storage
import datetime, time
import pytz

# emoji:  https://www.webfx.com/tools/emoji-cheat-sheet/
user_timezone = "Asia/Yekaterinburg"


# type of log records
class RecordType:
    CameToWork = 1
    LeftWork = 2
    StayedAtHome = 3


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
        get_confirmation_msg(user_id, first_name, RecordType.StayedAtHome),
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
        get_confirmation_msg(user_id, first_name, RecordType.CameToWork),
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
        get_confirmation_msg(user_id, first_name, RecordType.LeftWork),
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
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    keyboard = [
        [
            InlineKeyboardButton("Came to work", callback_data=RecordType.CameToWork),
            InlineKeyboardButton("Left work", callback_data=RecordType.LeftWork),
            InlineKeyboardButton("Stayed at home", callback_data=RecordType.StayedAtHome),
        ],
        [InlineKeyboardButton("Display stats", callback_data='stats')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.chat.send_message(
        f'<a href="tg://user?id={user_id}">{first_name}</a>, please choose one option:',
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup)


# function to handle buttons
def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    user_id = query.from_user.id
    user_name = query.from_user.first_name

    match query.data:
        case 'stats':
            msg = get_stats_formatted_for_chat(query.message.chat.id)
            query.edit_message_text(
                text=msg,
                parse_mode=ParseMode.HTML,
                reply_markup=None)
        case '...':
            pass
        case _:
            if query.data.isdigit():
                record_type = int(query.data)
                storage.update_record(
                    chat_id=query.message.chat.id,
                    user_id=user_id,
                    user_name=user_name,
                    time_stamp=query.message.date,
                    record_type=record_type)
                msg = get_confirmation_msg(user_id, user_name, record_type)
                query.edit_message_reply_markup(None)
                query.edit_message_text(
                    text=msg,
                    parse_mode=ParseMode.HTML)


# echo test
def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('sjdhahdjk')


# format log record
def format_record(record) -> str:
    # 0 - user_id, 1 - user_name, 2 - time_stamp, 3 - record_type
    msg = f'<a href="tg://user?id={record[0]}">{record[1]}</a> ';

    match record[3]:
        case RecordType.CameToWork:
            msg += 'came to work'
        case RecordType.LeftWork:
            msg += 'has left work'
        case RecordType.StayedAtHome:
            msg += 'stayed at home'
    timestamp = datetime.datetime.fromisoformat(str(record[2]))
    timezone_user = pytz.timezone(user_timezone)  # datetime.timezone(datetime.timedelta(hours=user_timezone), 'local')
    timezone_utc = pytz.timezone("UTC")

    timestamp_user = timestamp.astimezone(timezone_user)
    timestamp_user_str = timestamp_user.strftime('%Y-%m-%d %H:%M:%S')

    now = datetime.datetime.now(timezone_user)

    if timestamp_user.date() == now.date():
        timestamp_user_str = timestamp_user.strftime('%H:%M')
    elif timestamp_user.date() == (now.date() - datetime.timedelta(days=1)):
        timestamp_user_str = 'yesterday'
    elif timestamp_user.date() < (now.date() - datetime.timedelta(days=1)):
        timestamp_user_str = 'earlier'
    else:
        timestamp_user_str = 'time traveller!'

    msg += f'\n<i>{timestamp_user_str}</i>'
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
    return emojize(
        msg,
        use_aliases=True)


# get user confirmation message in html format (with emoji)
def get_confirmation_msg(user_id: int, user_name: str, record_type: RecordType) -> str:
    match record_type:
        case RecordType.CameToWork:
            return emojize(
                f'<a href="tg://user?id={user_id}">{user_name}</a> :office: :thumbsup:',
                use_aliases=True)
        case RecordType.LeftWork | RecordType.StayedAtHome:
            return emojize(
                f'<a href="tg://user?id={user_id}">{user_name}</a> :house: :thumbsup:',
                use_aliases=True)
        case _:
            return "error"
