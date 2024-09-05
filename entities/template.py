# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Template(BaseModel):
    cr17a_id: str
    cr17a_name: str
