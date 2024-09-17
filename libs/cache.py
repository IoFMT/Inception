# -*- coding: utf-8 -*-

import json
import sqlite3

from libs import config

db = None


def initialize_db():
    global db
    if db is None:
        db = sqlite3.connect(config.CACHE_DB)
        cursor = db.cursor()
        cursor.execute(config.CACHE_SQL_TABLE)
        db.commit()
    return db.cursor()


def select(user_id, sharelink_id, schedule_id=None, type=None):
    global db
    cursor = initialize_db()

    query = None
    parameters = None
    records = None

    if schedule_id is not None and type is not None:
        query = "SELECT * FROM sfg20_data WHERE user_id = ? and sharelink_id = ? and schedule_id = ? and type = ?"
        parameters = (user_id, sharelink_id, schedule_id, type)
    elif schedule_id is not None and type is None:
        query = "SELECT * FROM sfg20_data WHERE user_id = ? and sharelink_id = ? and schedule_id = ?"
        parameters = (schedule_id,)
    else:
        query = "SELECT * FROM sfg20_data WHERE user_id = ? and sharelink_id = ?"
        parameters = (user_id, sharelink_id)

    records = cursor.execute(query, parameters).fetchall()

    return records


def save(data):
    global db
    cursor = initialize_db()
    cursor.execute(
        config.CACHE_SQL_DELETE,
        (
            data["schedule"][0]["user_id"],
            data["schedule"][0]["sharelink_id"],
            data["schedule"][0]["schedule_id"],
        ),
    )
    for key in data:
        for item in data[key]:
            cursor.execute(
                config.CACHE_SQL_INSERT,
                (
                    item["user_id"],
                    item["sharelink_id"],
                    item["schedule_id"],
                    item["type"],
                    json.dumps(item["data"]),
                ),
            )
    db.commit()


def clear(user_id):
    global db
    cursor = initialize_db()
    cursor.execute(
        config.CACHE_SQL_CLEAR,
        (user_id),
    )
