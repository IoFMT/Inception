# -*- coding: utf-8 -*-

from pydantic import BaseModel


class SearchTerm(BaseModel):
    term: str
