#!/usr/bin/env python

# main.py
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, executor, types

import commands as cmd
import filters
import persistent as pers
import messages as msg


api_token = os.environ['TOKEN']

logging.basicConfig(level=logging.INFO)
bot = Bot(token=api_token)
dp = Dispatcher(bot)
dp.filters_factory.bind(filters.PrivateFilter)


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    await cmd.start_conversation(message)


@dp.message_handler(commands=['help'])
async def info(message: types.Message):
    await cmd.info(message)


# @dp.message_handler(is_private=True, commands=['came', 'left', 'stay'])
@dp.message_handler(commands=['came', 'left', 'stay'])
async def on_set_status_group(message: types.Message):
    await cmd.set_status(message)


@dp.message_handler(commands=['stats'])
async def on_get_status(message: types.Message):
    await cmd.get_statuses(message)


async def on_startup(x):
    await pers.prepare()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
