#!/usr/bin/env python

import aiosqlite
import asyncio
import datetime
import enum_defs
import os
from typing import Tuple

__dbpath = os.environ['DBPATH']
__query_records_create = '''
CREATE TABLE IF NOT EXISTS records (
    id          INTEGER  PRIMARY KEY AUTOINCREMENT
                         UNIQUE
                         NOT NULL,
    chat_id     INTEGER  NOT NULL,
    user_id     INTEGER  NOT NULL,
    time_stamp  DATETIME NOT NULL,
    record_type INTEGER  NOT NULL,
    UNIQUE (
        chat_id,
        user_id
    )
    ON CONFLICT REPLACE
);'''
__query_selchats_create = '''
CREATE TABLE IF NOT EXISTS user_selected_chat (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL
                    UNIQUE ON CONFLICT REPLACE,
    chat_id INTEGER NOT NULL
);
'''
__query_tables_exists = '''
SELECT count(*) FROM sqlite_master WHERE type='table' AND name in ('records', 'user_selected_chat')
'''


async def __check_file_exists(db_file) -> bool:
    if not os.path.isfile(db_file):
        return False
    async with aiosqlite.connect(db_file) as db:
        async with db.execute(__query_tables_exists) as cursor:
            # async with cursor.fetchone() as row:
            async for row in cursor:
                result = row[0] == 2
    return result


async def __create_file(db_file) -> None:
    async with aiosqlite.connect(db_file) as db:
        await db.execute(__query_records_create)
        await db.execute(__query_selchats_create)
        await db.commit()


async def prepare() -> None:
    exists = await __check_file_exists(__dbpath)
    if not exists:
        await __create_file(__dbpath)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


async def set_status(
        user_id: int,
        chat_id: int,
        time_stamp: datetime,
        record_type: enum_defs.RecordType) -> None:
    async with aiosqlite.connect(__dbpath) as db:
        await db.execute(
            'insert into records (chat_id, user_id, time_stamp, record_type) values (?, ?, ?, ?)',
            [chat_id, user_id, time_stamp, record_type.value]
        )
        await db.commit()


async def get_statuses(chat_id: int):
    async with aiosqlite.connect(__dbpath) as db:
        db.row_factory = dict_factory
        async with db.execute(
                'select user_id, time_stamp, record_type from records where chat_id = ? order by time_stamp desc',
                [chat_id]
        ) as cursor:
            records = await cursor.fetchall()

    return records


async def get_user_group(
        user_id: int) -> Tuple[bool, int]:
    is_found = False
    chat_id = 0
    async with aiosqlite.connect(__dbpath) as db:
        async with db.execute(
                'select chat_id from user_selected_chat where user_id = ?',
                [user_id]
        ) as cursor:
            row = await cursor.fetchone()
            if row is not None:
                is_found = True
                chat_id = row[0]
    return is_found, chat_id


async def set_user_group(
        user_id: int,
        chat_id: int) -> None:
    async with aiosqlite.connect(__dbpath) as db:
        await db.execute(
            'insert into user_selected_chat (chat_id, user_id) values (?, ?)',
            [chat_id, user_id]
        )
        await db.commit()

# asyncio.run(__prepare())
