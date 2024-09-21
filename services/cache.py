# -*- coding: utf-8 -*-

import json

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


from libs import config
from entities.sfg20 import CacheParameters, Entities
from entities.base import Config

engine = None
SessionLocal = None


def get_db():
    global engine, SessionLocal

    if engine is None:
        engine = create_engine(config.CACHE_DB)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print("Creating cache database")
        db1 = SessionLocal()
        db1.execute(text(config.CACHE_SQL_CREATE))
        db1.commit()
        db1.close()
        print("Cache database created")

    db = SessionLocal()
    return db


def list_cache(item: CacheParameters):
    db = get_db()

    stmt = None

    if item.schedule_id is not None and (
        item.type is not None and item.type != Entities.all
    ):
        stmt = text(
            "SELECT * FROM sfg20_data WHERE user_id = :p1 AND sharelink_id = :p2 AND schedule_id = :p3 AND type = :p4"
        )
        stmt = stmt.bindparams(
            p1=item.user_id, p2=item.sharelink_id, p3=item.schedule_id, p4=item.type
        )
    elif item.schedule_id is not None and (
        item.type is None or item.type == Entities.all
    ):
        stmt = text(
            "SELECT * FROM sfg20_data WHERE user_id = :p1 and sharelink_id = :p2 and schedule_id = :p3"
        )
        stmt = stmt.bindparams(
            p1=item.user_id, p2=item.sharelink_id, p3=item.schedule_id
        )
    else:
        stmt = text(
            "SELECT * FROM sfg20_data WHERE user_id = :p1 and sharelink_id = :p2"
        )
        stmt = stmt.bindparams(p1=item.user_id, p2=item.sharelink_id)

    records = db.execute(stmt).fetchall()
    response = []
    for record in records:
        response.append(json.loads(record[4]))
    return response


def save_cache(data):
    db = get_db()

    print("Deleting cache data")
    stmt_delete = text(config.CACHE_SQL_DELETE)
    stmt_delete = stmt_delete.bindparams(
        p1=data["schedule"][0]["user_id"],
        p2=data["schedule"][0]["sharelink_id"],
        p3=data["schedule"][0]["schedule_id"],
    )
    db.execute(stmt_delete)

    print("Inserting cache data")
    for key in data:
        for item in data[key]:
            stmt_insert = text(config.CACHE_SQL_INSERT)
            stmt_insert = stmt_insert.bindparams(
                p1=item["user_id"],
                p2=item["sharelink_id"],
                p3=item["schedule_id"],
                p4=item["type"],
                p5=json.dumps(item),
            )
            db.execute(stmt_insert)

    db.commit()


def clear_cache(user_id):
    db = get_db()
    stmt = text(config.CACHE_SQL_CLEAR)
    stmt = stmt.bindparams(p1=user_id)
    db.execute(stmt)


def add_config(data: Config):
    db = get_db()

    stmt = text(config.CACHE_SQL_INSERT_CONFIG)
    stmt = stmt.bindparams(
        p1=data.api_key,
        p2=data.customer_name,
        p3=data.access_token,
        p4=data.shared_links,
    )
    db.execute(stmt)
    db.commit()


def delete_config(api_key):
    db = get_db()
    stmt = text(config.CACHE_SQL_DELETE_CONFIG)
    stmt = stmt.bindparams(p1=api_key)
    db.execute(stmt)
    db.commit()


def select_config(api_key):
    db = get_db()

    stmt = None
    if api_key == "all":
        stmt = text(
            "SELECT api_key, customer_name, access_token, shared_links FROM config"
        )
    else:
        stmt = text("SELECT access_token, shared_links FROM config WHERE api_key = :p1")
        stmt = stmt.bindparams(p1=api_key)

    result = db.execute(stmt).fetchall()

    results = []
    for res in result:
        raw_shared_links = [item for item in res[1].split(",")]
        shared_links = []
        if api_key != "all":
            for item in raw_shared_links:
                record = {}
                if "#" in item:
                    record["id"] = item.split("#")[0]
                    record["name"] = item.split("#")[1]
                else:
                    record["id"] = item
                    record["name"] = "Name not provided"
                record["url"] = (
                    "https://www.demo.facilities-iq.com/app/facilities?share={0}".format(
                        record["id"]
                    )
                )
                shared_links.append(record)
            results.append({"access_token": res[0], "shared_links": shared_links})
        else:
            results.append(
                {
                    "api_key": res[0],
                    "customer_name": res[1],
                    "access_token": res[2],
                    "shared_links": res[3],
                }
            )

    return results
