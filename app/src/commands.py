#!/usr/bin/env python

from aiogram import types, utils, Bot
import persistent as pers
from enum_defs import RecordType
import messages as msg


async def is_i_am_admin(message: types.Message) -> bool:
    me = await message.bot.get_chat_member(
        chat_id=message.chat.id,
        user_id=message.bot.id)
    return me.is_chat_admin()


async def send_reply(
        message: types.Message,
        text: str) -> None:
    user = message.from_user
    is_admin = await is_i_am_admin(message)
    is_private = message.chat.type == types.ChatType.PRIVATE

    if is_private:
        '''
        in private chat just send a reply
        '''
        await message.reply(
            text=text,
            parse_mode=types.ParseMode.HTML)
    else:
        '''
        in group chat
          forward original message to private chat
          send reply to private chat
          remove original message from group chat, if allowed
        '''
        try:
            await message.forward(user.id)
            await message.chat.bot.send_message(
                chat_id=user.id,
                text=text,
                parse_mode=types.ParseMode.HTML)
        except utils.exceptions.BotBlocked:
            await message.reply("Bot blocked!")
        except utils.exceptions.CantInitiateConversation:
            await message.reply("Can't initiate private chat!")

        if is_admin:
            await message.delete()


async def is_user_member_of_chat(
        chat_id: int,
        user_id: int) -> bool:
    bot = Bot.get_current()
    member = await bot.get_chat_member(
        chat_id=chat_id,
        user_id=user_id)

    if member is None:
        return False
    return member.is_chat_member()


async def set_status(message: types.Message) -> None:
    chat = message.chat
    user = message.from_user
    is_private = message.chat.type == types.ChatType.PRIVATE
    rtypes = {
        '/stay': RecordType.StayedAtHome,
        '/came': RecordType.CameToWork,
        '/left': RecordType.LeftWork,
    }

    rtypes2 = [val for key, val in rtypes.items() if message.text.startswith(key)]

    if rtypes2 is None or len(rtypes2) == 0 or rtypes2[0] is None:
        await message.reply('Unknown command!')
        return

    rtype = rtypes2[0]

    if is_private:
        is_found, selected_chat_id = await pers.get_user_group(user.id)
        if not is_found:
            await send_reply(
                message=message,
                text=msg.chat_not_selected
            )
            return
    else:
        selected_chat_id = chat.id

    await pers.set_status(
        chat_id=selected_chat_id,
        user_id=user.id,
        time_stamp=message.date,
        record_type=rtype
    )

    await send_reply(
        message=message,
        text=msg.confirmation(user, rtype)
    )


async def get_statuses(message: types.Message) -> None:
    user = message.from_user
    is_found, selected_chat_id = await pers.get_user_group(user.id)

    if not is_found:
        await send_reply(
            message=message,
            text=msg.chat_not_selected
        )
        return

    statuses = await pers.get_statuses(selected_chat_id)

    if statuses is None:
        await send_reply(
            message=message,
            text='There are no records was found.'
        )
        return

    text = await msg.format_statuses(
        message.bot,
        selected_chat_id,
        statuses)

    await send_reply(
        message=message,
        text=text
    )


async def start_conversation(message: types.Message) -> None:
    is_private = message.chat.type == types.ChatType.PRIVATE

    if not is_private:
        await pers.set_user_group(
            user_id=message.from_user.id,
            chat_id=message.chat.id
        )
    await send_reply(
        message=message,
        text=msg.start_message
    )


async def info(message: types.Message) -> None:
    await send_reply(
        message=message,
        text=msg.help_message
    )
