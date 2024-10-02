# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum


class Result(BaseModel):
    status: str = Field(title="Status", description="The status of the request")
    message: str = Field(title="Message", description="The message of the request")
    data: list[dict] = Field(title="Data", description="The data of the request")


class Config(BaseModel):
    api_key: str = Field(
        title="API Key",
        description="The newly generated API Key",
    )
    customer_name: str = Field(
        title="Customer Name", description="The name of the SFG20 customer"
    )
    access_token: str = Field(
        title="Access Token",
        description="The Access Token provided by SFG20",
    )
    sfg_environment: str = Field(
        title="SFG Environment", description="The SFG20 environment"
    )


class SharedLinks(BaseModel):
    api_key: str = Field(title="API Key", description="The generated API Key")
    id: str = Field(title="ID", description="The ID of the SFG20 shared link")
    link_name: str = Field(title="Link Name", description="The name of the shared link")
    url: str = Field(title="URL", description="The URL of the shared link")


class SearchTerm(BaseModel):
    sharelink_id: str = Field(
        title="Sharelink ID", description="The ID of the SFG20 sharelink"
    )
    access_token: str = Field(
        title="Access Token",
        description="The Access Token provided by SFG20",
    )
    user_id: str = Field(title="User ID", description="The ID of the user")
    changes_since: str | None = Field(
        None,
        title="Changes Since",
        description="The date of changes since the last update",
    )
    order_field: str | None = Field(
        None, title="Order Field", description="The field to order the data by"
    )
    order_direction: Literal["asc", "Asc", "ASC", "desc", "Desc", "DESC"] | None = (
        Field(
            None,
            title="Order Direction",
            description="The direction to order the data by",
        )
    )


class Entities(str, Enum):
    all = "all"
    schedules = "schedules"
    assets = "assets"
    tasks = "tasks"
    frequencies = "frequencies"
    skills = "skills"
    classifications = "classifications"


class sfg20_data(BaseModel):
    user_id: str = Field(title="User ID", description="The ID of the user")
    sharelink_id: str = Field(
        title="Sharelink ID", description="The ID of the SFG20 sharelink"
    )
    schedule_id: str = Field(
        title="Schedule ID", description="The ID of the SFG20 schedule"
    )
    type: Entities = Field(
        title="Type",
        description="The type of the entity",
    )
    data: str = Field(
        title="Data",
        description="The data of the entity",
    )


class CacheParameters(BaseModel):
    user_id: str = Field(
        title="User ID", description="The ID of the user", example="admin@iofmt.com"
    )
    sharelink_id: str = Field(
        title="Sharelink ID", description="The ID of the SFG20 sharelink"
    )
    schedule_id: str | None = Field(
        None, title="Schedule ID", description="The ID of the SFG20 schedule"
    )
    type: Entities | None = Field(
        None, title="Type", description="The type of the entity", example="schedules"
    )
    order_field: str | None = Field(
        None, title="Order Field", description="The field to order the data by"
    )
    order_direction: Literal["asc", "Asc", "ASC", "desc", "Desc", "DESC"] | None = (
        Field(
            None,
            title="Order Direction",
            description="The direction to order the data by",
        )
    )


class Task(BaseModel):
    sharelink_id: str = Field(
        title="Shared Link ID", description="The ID of the shared link"
    )
    access_token: str = Field(
        title="Access Token", description="The Access Token provided by SFG20"
    )
    asset_id: str = Field(title="Asset ID", description="The ID of the asset")
    asset_index: int = Field(title="Asset Index", description="The index of the asset")
    task_id: str = Field(title="Task ID", description="The ID of the task")
    completion_date: str = Field(
        title="Completion Date", description="The date of completion"
    )


class TaskGroupItem(BaseModel):
    task_id: str = Field(title="Task ID", description="The ID of the task")
    duration_minutes: int = Field(
        title="Duration Minutes", description="The duration of the task in minutes"
    )
    completion_date: str = Field(
        title="Completion Date", description="The date of completion"
    )


class TaskGroup(BaseModel):
    sharelink_id: str = Field(
        title="Shared Link ID", description="The ID of the shared link"
    )
    access_token: str = Field(
        title="Access Token", description="The Access Token provided by SFG20"
    )
    completion_date: str = Field(
        title="Completion Date", description="The date of completion"
    )
    schedule_id: str = Field(title="Schedule ID", description="The ID of the schedule")
    visit: str | None = Field(None, title="Visit", description="The visit number")
    asset_id: str = Field(title="Asset ID", description="The ID of the asset")
    tasks_completed: list[TaskGroupItem] = Field(
        title="Tasks Completed", description="The tasks completed"
    )


class ConfigSharedLinks(BaseModel):
    sharelink_id: str = Field(
        title="Sharelink ID", description="The ID of the SFG20 sharelink"
    )
    access_token: str = Field(
        title="Access Token",
        description="The Access Token provided by SFG20",
    )
