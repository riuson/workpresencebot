#!/usr/bin/env python

import sqlite3, os
from sqlite3 import Error

dbpath = os.environ['DBPATH']


# check if database exists
def check_file(db_file) -> bool:
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    # get the count of tables with the name
    cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='records' ''')

    # if the count is 1, then table exists
    result = False
    if cursor.fetchone()[0] == 1:
        print('Table exists.')
        result = True

    # commit the changes to db
    connection.commit()
    # close the connection
    connection.close()
    return result


# create database
def create_file(db_file) -> None:
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    # create table
    cursor.execute('''CREATE TABLE records (
    id          INTEGER  PRIMARY KEY AUTOINCREMENT
                         UNIQUE
                         NOT NULL,
    chat_id     INTEGER  NOT NULL,
    user_id     INTEGER  NOT NULL,
    user_name   STRING,
    time_stamp  DATETIME NOT NULL,
    record_type INTEGER  NOT NULL,
    UNIQUE (
        chat_id,
        user_id
    )
    ON CONFLICT REPLACE
);''')

    # commit the changes to db
    connection.commit()
    # close the connection
    connection.close()


# get records for chat
def get_records(chat_id):
    connection = sqlite3.connect(dbpath, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(
        'select user_id, user_name, time_stamp, record_type from records where chat_id = ? order by time_stamp desc',
        [chat_id])
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


if not check_file(dbpath):
    create_file(dbpath)
