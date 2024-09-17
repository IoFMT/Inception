# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Result(BaseModel):
    status: str
    message: str
    data: list[dict]
