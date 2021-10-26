#!/usr/bin/env python

import sqlite3, os

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

dbpath = os.environ['DBPATH']

# get records for chat
def get_records(chat_id):
    connection = sqlite3.connect(dbpath, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute('select user_id, user_name, time_stamp, record_type from records where chat_id = ? order by time_stamp desc', [chat_id])
    table = cursor.fetchall()
    connection.close()
    return table


# update record in table
def update_record(chat_id, user_id, user_name, time_stamp, record_type):
    connection = sqlite3.connect(dbpath, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(
        'insert into records (chat_id, user_id, user_name, time_stamp, record_type) values (?, ?, ?, ?, ?)',
        [chat_id, user_id, user_name, time_stamp, record_type])
    connection.commit()
    connection.close()
