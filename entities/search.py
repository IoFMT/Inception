# -*- coding: utf-8 -*-

from pydantic import BaseModel
from enum import Enum


class SearchTerm(BaseModel):
    term: str


class Entities(str, Enum):
    all = "all"
    schedules = "schedules"
    assets = "assets"
    tasks = "tasks"
    frequencies = "frequencies"
    skills = "skills"
    classifications = "classifications"
