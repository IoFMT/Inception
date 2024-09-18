# -*- coding: utf-8 -*-

import datetime
from enum import Enum
from pydantic import BaseModel


class Tables(str, Enum):
    report = "cr17a_pub_siteainspectionreports_headers"
    task = "cr17a_pub_siteainspectionreports_items"


class Template(BaseModel):
    table_name: str
    key_field: str
    key_value: str


class Report(BaseModel):
    cr17a_reportuid: str
    cr17a_sharinglinkid: str
    cr17a_templateid: str
    cr17a_templatename: str
    cr17a_templatenamecustom: str
    cr17a_templateserviceroutine: str
    cr17a_templateversion: str
    cr17a_templatemodifieddate: datetime.datetime


class Task(BaseModel):
    cr17a_reportuid: str
    cr17a_sharinglinkid: str
    cr17a_taskscheduletemplatetitle: str
    cr17a_taskscheduletemplateid: str
    cr17a_templatenamecustom: str
    cr17a_taskid: str
    cr17a_tasktitle: str
    cr17a_taskversion: str
    cr17a_taskmodifieddate: datetime.datetime
    cr17a_taskurl: str
    cr17a_tasklinksmartwords: str
    cr17a_tasksmartwords: str
    cr17a_tasktiming: str
    cr17a_taskserviceroutinecode: str
    cr17a_taskfrequencyperiod: str
    cr17a_taskfrequencyinterval: str
    cr17a_taskcriticalityclass: str
    cr17a_taskskillset: str
    cr17a_taskdetailsactivities: str
