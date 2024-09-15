# -*- coding: utf-8 -*-

import base64
import json
import sqlite3
from libs import config
import requests

# Database Object
db = None


def save_data(cursor, data, key, type):
    """ """
    results = []
    for row in data:
        record = {}
        for field in config.CACHE_DB_FIELDS[type]:
            if "." in field:
                field_parts = field.split(".")
                if row[field_parts[0]] is not None:
                    record[field_parts[1]] = row[field_parts[0]][field_parts[1]] or None
                record[field_parts[1]] = None
            else:
                record[field] = row[field]

        b64_record = base64.b64encode(json.dumps(record).encode()).decode()
        sqlcount = cursor.execute(
            "SELECT COUNT(*) FROM sfg20_data WHERE schedule_id = ? and type = ? and sha = ?",
            (key, type, b64_record),
        ).fetchone()[0]
        if sqlcount == 0:
            cursor.execute(
                "INSERT INTO sfg20_data (schedule_id, type, data, sha) VALUES (?, ?, ?, ?)",
                (key, type, json.dumps(record), b64_record),
            )
        else:
            cursor.execute(
                "UPDATE sfg20_data SET data = ? WHERE schedule_id = ? and type = ? and sha = ?",
                (json.dumps(record), key, type, b64_record),
            )
        results.append(record)

    return results


def list_data(schedule_id=None, type=None):
    global db
    cursor = None

    if db is None:
        db = sqlite3.connect(config.CACHE_DB)
        cursor = db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS sfg20_data (schedule_id INTEGER, type TEXT, data TEXT, sha TEXT)"
        )
    else:
        cursor = db.cursor()

    query = None
    parameters = None
    records = None

    if schedule_id is not None and type is not None:
        query = "SELECT * FROM sfg20_data WHERE schedule_id = ? and type = ?"
        parameters = (schedule_id, type)
    elif schedule_id is not None and type is None:
        query = "SELECT * FROM sfg20_data WHERE schedule_id = ?"
        parameters = (schedule_id,)
    else:
        query = "SELECT * FROM sfg20_data"

    if parameters:
        records = cursor.execute(query, parameters).fetchall()
    else:
        records = cursor.execute(query).fetchall()

    response = []
    for record in records:
        if schedule_id is not None and type is not None:
            response.append(json.loads(record[2]))
        else:
            response.append(
                {
                    "schedule_id": record[0],
                    "type": record[1],
                    "data": json.loads(record[2]),
                }
            )
    return response


def retrieve_all_data():
    global db
    query = config.SFG20_QUERY_001.format(
        config.SFG20_SHARE_ID, config.SFG20_ACCESS_TOKEN
    )

    body = {
        "query": query,
    }

    response = requests.post(config.SFG20_URL, json=body)
    if response.status_code == 200:
        cursor = None
        if db is None:
            db = sqlite3.connect(config.CACHE_DB)
            cursor = db.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS sfg20_data (schedule_id INTEGER, type TEXT, data TEXT, sha TEXT)"
            )
        else:
            cursor = db.cursor()

        all_data = response.json()["data"]["regime"]["schedules"]
        schedules = []
        for raw_data in all_data:
            schedule = save_data(cursor, [raw_data], raw_data["id"], "schedules")
            save_data(cursor, raw_data["skills"], raw_data["id"], "skills")
            save_data(cursor, raw_data["tasks"], raw_data["id"], "tasks")
            save_data(cursor, raw_data["assets"], raw_data["id"], "assets")
            save_data(cursor, raw_data["frequencies"], raw_data["id"], "frequencies")
            save_data(cursor, raw_data["tasks"], raw_data["id"], "classification")
            db.commit()
            schedules += schedule
    return schedules
