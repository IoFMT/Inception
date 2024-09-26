# -*- coding: utf-8 -*-

import json
import requests

from libs import config
from entities.base import SearchTerm, Task, TaskGroup
import cache


def parse_data(data, user, sharelink, key, type):
    results = []
    for row in data:
        record = {
            "user_id": user,
            "sharelink_id": sharelink,
            "schedule_id": key,
            "type": type,
        }

        for field in config.CACHE_DB_FIELDS[type]:
            if "." in field:
                field_parts = field.split(".")
                if row[field_parts[0]] is not None:
                    record[field_parts[1]] = row[field_parts[0]][field_parts[1]] or None
                else:
                    record[field_parts[1]] = None
            else:
                record[field] = row[field]

        if type == "tasks":
            if len(record["id"].split(".")) == 4:
                record["task_number"] = int(record["id"].split(".")[3]) + 1
            else:
                record["task_number"] = 1
        results.append(record)

    results = [json.loads(x) for x in set([json.dumps(d) for d in results])]
    return results


def retrieve_all_data(searchItem: SearchTerm, environment: str):
    since_date = searchItem.changes_since
    if searchItem.changes_since is None:
        since_date = "2000-01-01T00:00:00Z"

    query = config.SFG20_QUERY_001.format(
        searchItem.sharelink_id, searchItem.access_token, since_date
    )

    body = {
        "query": query,
    }

    response = requests.post(config.SFG20_ENVS[environment], json=body)
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
            schedules.append(content)

    return schedules


def complete_task(task: Task, environment: str):
    query = config.SFG20_QUERY_003.format(
        task.sharelink_id,
        task.access_token,
        task.asset_id,
        task.asset_index,
        task.task_id,
        task.completion_date,
    )

    body = {
        "query": query,
    }

    response = requests.post(config.SFG20_ENVS[environment], json=body)
    return response.json()


def complete_task_group(task: TaskGroup, environment: str):
    items = []
    for item in task.tasks_completed:
        record = config.SFG20_QUERY_003_ITEM.format(
            item.task_id, item.duration_minutes, item.completion_date
        )
        items.append(record)

    items_formatted = " \n".join(items)

    query = config.SFG20_QUERY_003.format(
        task.sharelink_id,
        task.access_token,
        task.completion_date,
        task.schedule_id,
        task.visit,
        task.asset_id,
        items_formatted,
    )

    print(query)

    body = {
        "query": query,
    }

    response = requests.post(config.SFG20_ENVS[environment], json=body)
    return response.json()
