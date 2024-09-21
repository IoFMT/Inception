# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Result(BaseModel):
    status: str
    message: str
    data: list[dict]


class Config(BaseModel):
    api_key: str
    customer_name: str
    access_token: str
    shared_links: str
