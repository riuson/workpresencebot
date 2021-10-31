#!/usr/bin/env python

from enum_defs import RecordType
from aiogram import types, Bot
from emoji import emojize
import datetime
import pytz

start_message = """\
Hello, bot is online. 
"""

help_message = """\
/start - Start interaction with bot.
/help - Display this help message.
/came - User came to work. 
/left - User has left work. 
/stay - User stayed at home.
/stats - Display stati 
"""

user_timezone = "Asia/Yekaterinburg"

chat_not_selected = 'You have not chosen a chat.\nUse /start command in desired chat.'


def confirmation(user: types.User, record_type: RecordType) -> None:
    match record_type:
        case RecordType.CameToWork:
            action = 'You came to the work :office: :thumbsup:'
        case RecordType.LeftWork:
            action = 'You has left the work :house: :thumbsup:'
        case RecordType.StayedAtHome:
            action = 'You stayed at home :house: :thumbsup:'
    # result = f'<a href="tg://user?id={user.id}">{user.username}</a> {action}'
    return emojize(
        action,
        use_aliases=True)


def __format_status(
        user: types.User,
        timestamp: datetime) -> str:
    timezone_user = pytz.timezone(user_timezone)
    timestamp_user = timestamp.astimezone(timezone_user)
    now = datetime.datetime.now(timezone_user)

    if timestamp_user.date() == now.date():
        timestamp_user_str = timestamp_user.strftime('%H:%M')
    elif timestamp_user.date() == (now.date() - datetime.timedelta(days=1)):
        timestamp_user_str = 'yesterday'
    elif timestamp_user.date() < (now.date() - datetime.timedelta(days=1)):
        timestamp_user_str = 'earlier'
    else:
        timestamp_user_str = 'time traveller!'
    first_name = user.first_name if user.first_name is not None else '???'
    last_name = ' ' + user.last_name if user.last_name is not None else ''
    username = ' (@' + user.username + ')' if user.username is not None else ''
    return f'<a href="tg://user?id={user.id}">{first_name}{last_name}</a> {username}\n{timestamp_user_str}'


async def format_statuses(
        bot: Bot,
        chat_id: int,
        statuses) -> str:
    work = ''
    home = ''
    for status in statuses:
        member = await bot.get_chat_member(chat_id, int(status['user_id']))
        record_type = RecordType(int(status['record_type']))
        timestamp = datetime.datetime.fromisoformat(str(status['time_stamp']))
        if record_type == RecordType.CameToWork:
            work += __format_status(member.user, timestamp) + '\n'
        else:
            home += __format_status(member.user, timestamp) + '\n'

    msg = ""
    if work != "":
        msg = "<b>At work</b> :office:\n" + work
    if home != "":
        if work != "":
            msg += "\n"
        msg += "<b>At home</b> :house:\n" + home

    if msg == "":
        msg = "No records was found!"
    return emojize(
        msg,
        use_aliases=True)
