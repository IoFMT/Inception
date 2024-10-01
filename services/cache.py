# -*- coding: utf-8 -*-

import json

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


from libs import config
from entities.base import Config, CacheParameters, Entities, SharedLinks

engine = None
SessionLocal = None


def get_db():
    global engine, SessionLocal

    if engine is None:
        engine = create_engine(config.CACHE_DB)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db1 = SessionLocal()
        db1.execute(text(config.CACHE_SQL_CREATE))
        db1.commit()
        db1.close()

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

    if item.order_field is not None:
        if item.order_direction is not None and item.order_direction == "desc":
            response = sorted(response, key=lambda x: x[item.order_field], reverse=True)
        else:
            response = sorted(response, key=lambda x: x[item.order_field])

    return response


def save_cache(data):
    db = get_db()

    stmt_delete = text(config.CACHE_SQL_DELETE)
    stmt_delete = stmt_delete.bindparams(
        p1=data["schedule"][0]["user_id"],
        p2=data["schedule"][0]["sharelink_id"],
        p3=data["schedule"][0]["schedule_id"],
    )
    db.execute(stmt_delete)

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
        p4=data.sfg_environment,
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
            "SELECT api_key, customer_name, access_token, sfg_environment FROM config"
        )
    else:
        stmt = text(
            "SELECT api_key, customer_name, access_token, sfg_environment FROM config WHERE api_key = :p1"
        )
        stmt = stmt.bindparams(p1=api_key)

    result = db.execute(stmt).fetchall()

    results = []
    for res in result:
        results.append(
            {
                "api_key": res[0],
                "customer_name": res[1],
                "access_token": res[2],
                "sfg_environment": res[3],
            }
        )

    return results


def select_shared_links(api_key):
    db = get_db()

    stmt = text(
        "SELECT id, link_name, url FROM config_shared_links WHERE api_key = :p1"
    )
    stmt = stmt.bindparams(p1=api_key)

    result = db.execute(stmt).fetchall()

    results = []
    for res in result:
        results.append({"id": res[0], "name": res[1], "url": res[2]})

    return results


def delete_shared_links(api_key, id):
    db = get_db()

    stmt = text(config.CACHE_SQL_DELETE_SHARED_LINKS)
    stmt = stmt.bindparams(p1=api_key, p2=id)

    db.execute(stmt)
    db.commit()


def add_shared_links(data):
    db = get_db()

    stmt = text(config.CACHE_SQL_INSERT_SHARED_LINKS)
    stmt = stmt.bindparams(p1=data.api_key, p2=data.id, p3=data.link_name, p4=data.url)
    db.execute(stmt)
    db.commit()


def update_shared_links(data: SharedLinks):
    db = get_db()

    stmt = text(config.CACHE_SQL_UPDATE_SHARED_LINKS)
    stmt = stmt.bindparams(p1=data.api_key, p2=data.id, p3=data.link_name, p4=data.url)
    db.execute(stmt)
    db.commit()


def get_environment(api_key):
    db = get_db()
    stmt = text(
        "SELECT api_key, customer_name, access_token, sfg_environment FROM config WHERE api_key = :p1"
    )
    stmt = stmt.bindparams(p1=api_key)

    result = db.execute(stmt).fetchone()
    return result[3]


def exists_shared_link(api_key, id):
    db = get_db()

    stmt = text(
        "SELECT count(1) as cnt FROM config_shared_links WHERE api_key = :p1 and id = :p2"
    )
    stmt = stmt.bindparams(p1=api_key, p2=id)
    result = db.execute(stmt).fetchone()
    return result[0] > 0
