# -*- coding: utf-8 -*-

from typing import Literal
from pydantic import BaseModel
from enum import Enum


class SearchTerm(BaseModel):
    sharelink_id: str
    access_token: str
    user_id: str
    changes_since: str | None = None


class Entities(str, Enum):
    all = "all"
    schedules = "schedules"
    assets = "assets"
    tasks = "tasks"
    frequencies = "frequencies"
    skills = "skills"
    classifications = "classifications"


class sfg20_data(BaseModel):
    user_id: str
    sharelink_id: str
    schedule_id: str
    type: Entities
    data: str


class CacheParameters(BaseModel):
    user_id: str
    sharelink_id: str
    schedule_id: str | None = None
    type: Entities | None = None
    order_field: str | None = None
    order_direction: Literal["asc", "Asc", "ASC", "desc", "Desc", "DESC"] | None = None
