# -*- coding: utf-8 -*-

from libs import config
import requests


def retrieve_data():
    query = config.SFG20_QUERY_001.format(
        config.SFG20_SHARE_ID, config.SFG20_ACCESS_TOKEN
    )

    body = {
        "query": query,
    }

    response = requests.post(config.SFG20_URL, json=body)

    return response.json()
