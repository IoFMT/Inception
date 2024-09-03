# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Template(BaseModel):
    template_id: int
    template_title: str
