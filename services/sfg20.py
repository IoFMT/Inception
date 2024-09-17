# -*- coding: utf-8 -*-

from html import entities
import json
import requests

from libs import config, cache
from entities.sfg20 import SearchTerm, Entities, CacheParameters


def parse_data(data, user, sharelink, key, type):
    results = []
    for row in data:
        record = {
            "user_id": user,
            "sharelink_id": sharelink,
            "schedule_id": key,
            "type": type,
            "data": {},
        }

        for field in config.CACHE_DB_FIELDS[type]:
            if "." in field:
                field_parts = field.split(".")
                if row[field_parts[0]] is not None:
                    record["data"][field_parts[1]] = (
                        row[field_parts[0]][field_parts[1]] or None
                    )
                else:
                    record["data"][field_parts[1]] = None
            else:
                record["data"][field] = row[field]
        results.append(record)

    results = [json.loads(x) for x in set([json.dumps(d) for d in results])]
    return results


def list_data(cacheParams: CacheParameters):
    records = cache.select(
        cacheParams.user_id,
        cacheParams.sharelink_id,
        cacheParams.schedule_id,
        cacheParams.type,
    )

    response = []
    for record in records:
        response.append(
            {
                "user_id": record[0],
                "sharelink_id": record[1],
                "schedule_id": record[2],
                "type": record[3],
                "data": json.loads(record[4]),
            }
        )
    return response


def retrieve_all_data(searchItem: SearchTerm):
    query = config.SFG20_QUERY_001.format(
        searchItem.sharelink_id, searchItem.access_token
    )

    body = {
        "query": query,
    }

    response = requests.post(config.SFG20_URL, json=body)
    if response.status_code == 200:
        all_data = response.json()["data"]["regime"]["schedules"]
        schedules = []
        for raw_data in all_data:
            content = dict(
                schedule=parse_data(
                    [raw_data],
                    searchItem.user_id,
                    searchItem.sharelink_id,
                    raw_data["id"],
                    "schedules",
                ),
                skills=parse_data(
                    raw_data["skills"],
                    searchItem.user_id,
                    searchItem.sharelink_id,
                    raw_data["id"],
                    "skills",
                ),
                tasks=parse_data(
                    raw_data["tasks"],
                    searchItem.user_id,
                    searchItem.sharelink_id,
                    raw_data["id"],
                    "tasks",
                ),
                assets=parse_data(
                    raw_data["assets"],
                    searchItem.user_id,
                    searchItem.sharelink_id,
                    raw_data["id"],
                    "assets",
                ),
                frequencies=parse_data(
                    raw_data["frequencies"],
                    searchItem.user_id,
                    searchItem.sharelink_id,
                    raw_data["id"],
                    "frequencies",
                ),
                classifications=parse_data(
                    raw_data["tasks"],
                    searchItem.user_id,
                    searchItem.sharelink_id,
                    raw_data["id"],
                    "classification",
                ),
            )
            cache.save(content)
            schedules += content["schedule"]
    return schedules


def clear_data(user_id: str):
    cache.delete(user_id)
    return []
