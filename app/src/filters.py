#!/usr/bin/env python

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class PrivateFilter(BoundFilter):
    key = 'is_private'

    def __init__(self, is_private):
        self.is_private = is_private

    async def check(self, message: types.Message):
        return message.chat.type == types.ChatType.PRIVATE
