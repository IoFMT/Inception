# -*- coding: utf-8 -*-

from pydantic import BaseModel
from enum import Enum


class SearchTerm(BaseModel):
    sharelink_id: str
    access_token: str
    user_id: str


class Entities(str, Enum):
    all = "all"
    schedules = "schedules"
    assets = "assets"
    tasks = "tasks"
    frequencies = "frequencies"
    skills = "skills"
    classifications = "classifications"


class CacheParameters(BaseModel):
    user_id: str
    sharelink_id: str
    schedule_id: str | None = None
    type: Entities | None = None
