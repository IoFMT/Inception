# -*- coding: utf-8 -*-
"""
    Main file to run the API
"""
from functools import wraps
import secrets
import traceback

from time import time
from typing import Annotated, Any


import requests
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates

from routers import security_router
from entities.base import (
    Config,
    Result,
    SharedLinks,
    CacheParameters,
    SearchTerm,
    Task,
    TaskGroup,
    ConfigSharedLinks,
)
from services import sfg20 as sv_sfg20
from services import cache
from libs import config
from libs.utils import decode, encode

# from entities.template import Template, Report, Task, Tables
# from services import dataverse as sv_dataverse


app = FastAPI(title="IoFMT REST API")
security = HTTPBasic()
templates = Jinja2Templates(directory="static")

# -------------------------------------------------
# Adding Middlewares
# -------------------------------------------------

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def time_call(request: Request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time()
    response.headers["X-Process-Time"] = str(process_time - start_time)
    return response


def rate_limited(max_calls: int, time_frame: int):
    """
    :param max_calls: Maximum number of calls allowed in the specified time frame.
    :param time_frame: The time frame (in seconds) for which the limit applies.
    :return: Decorator function.
    """

    def decorator(func):
        calls = []

        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time()
            calls_in_time_frame = [call for call in calls if call > now - time_frame]
            if len(calls_in_time_frame) >= max_calls:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded.",
                )
            calls.append(now)
            return await func(*args, **kwargs)

        return wrapper

    return decorator


# -------------------------------------------------
# Customizing OpenAPI definition
# We need to downgrade to 3.0.2 to be compatible
# with Power Platform Custom Connector
# -------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="IoFMT REST API",
        version="1.0.0",
        summary="This is a REST API for IoFMT Inception project",
        description="""This REST API acts as a Facade for connecting to SFG20 GraphAPI and maintain a cache to expedite performance.
        <br><br>
        This API is also mapped in a Power Platform Custom Connector.
        <br><br>
        To generate the API KEY for a customer, please go to: <a href='/admin' target='_blank'>Admin</a>""",
        routes=app.routes,
        openapi_version="3.0.2",
        tags=config.tags_metadata,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = config.ADMIN_USER.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = config.ADMIN_PWD.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


app.openapi = custom_openapi


# -------------------------------------------------
# Endpoints
# -------------------------------------------------
@app.get("/", tags=["Basic"], response_model=Result, operation_id="get_api_status")
async def get_api_status() -> Any:
    return {
        "status": "OK",
        "message": "IoFMT REST API is running",
        "data": [{"version": "1.0.0"}],
    }


@app.get("/admin", tags=["Basic"], response_class=HTMLResponse, include_in_schema=False)
@rate_limited(config.THROTTLE_RATE, config.THROTTLE_TIME)
async def admin(
    request: Request, username: Annotated[str, Depends(get_current_username)]
) -> Any:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "name": username,
            "master_api_key": decode(config.GLOBAL_API_KEY),
        },
    )


# -------------------------------------------------
# SFG20 endpoints
# -------------------------------------------------
@app.post(
    "/schedules",
    tags=["SFG20"],
    response_model=Result,
    description="Search SFG20 schedules according to the parameters provided and load into the cache",
    operation_id="get_schedules",
)
@rate_limited(config.THROTTLE_RATE_EXT, config.THROTTLE_TIME)
async def get_schedules(
    search: SearchTerm,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
) -> Any:
    status = "OK"
    message = "Data retrieved successfully from SFG20 and cached in the API"
    try:
        environment = cache.get_environment(api_key)
        raw_data = sv_sfg20.retrieve_all_data(search, environment)
        response = []

        for item in raw_data:
            cache.save_cache(item)
            response.append(item["schedule"][0])

        responses = response
        if len(response) > 0:
            if search.order_field is not None:
                if (
                    search.order_direction is not None
                    and search.order_direction == "desc"
                ):
                    responses = sorted(
                        response, key=lambda x: x[search.order_field], reverse=True
                    )
                else:
                    responses = sorted(response, key=lambda x: x[search.order_field])

    except Exception as e:
        status = "Error"
        message = "Error retrieving data from SFG20"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": responses}


@app.post(
    "/shared-links",
    tags=["SFG20"],
    response_model=Result,
    description="List the SFG20 shared links available for the user",
    operation_id="get_shared_links",
)
@rate_limited(config.THROTTLE_RATE, config.THROTTLE_TIME)
async def get_shared_links(
    item: ConfigSharedLinks,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
) -> Any:
    environment = cache.get_environment(api_key)
    raw_response = sv_sfg20.load_shared_links(item, api_key, environment)
    data = []
    for response in raw_response:
        share = SharedLinks(**response)
        if not cache.exists_shared_link(str(api_key), response["id"]):
            cache.add_shared_links(share)
        else:
            cache.update_shared_links(share)

        data.append(
            {
                "id": response["id"],
                "name": response["link_name"],
                "url": response["url"],
            }
        )

    return {
        "status": "OK",
        "message": "List of SFG20 shared links",
        "data": data,
    }


@app.post(
    "/task/complete",
    tags=["SFG20"],
    response_model=Result,
    description="Mark a task as completed in SFG20",
    operation_id="complete_task",
)
@rate_limited(config.THROTTLE_RATE_EXT, config.THROTTLE_TIME)
async def complete_task(
    task: Task,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
) -> Any:
    status = "OK"
    message = "Task marked as completed in SFG20"
    try:
        environment = cache.get_environment(api_key)
        resp = sv_sfg20.complete_task(task, environment)
        response = [resp]
    except Exception as e:
        status = "Error"
        message = "Error marking task as completed in SFG20"
        response = [{"error": str(e)}]
        print(traceback.format_exc())
    return {"status": status, "message": message, "data": response}


@app.post(
    "/task_group/complete",
    tags=["SFG20"],
    response_model=Result,
    description="Mark a group of tasks as completed in SFG20",
    operation_id="complete_task_group",
)
@rate_limited(config.THROTTLE_RATE_EXT, config.THROTTLE_TIME)
async def complete_task_group(
    task: TaskGroup,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
) -> Any:
    status = "OK"
    message = "Task marked as completed in SFG20"
    try:
        environment = cache.get_environment(api_key)
        resp = sv_sfg20.complete_task_group(task, environment)
        response = [resp]
    except Exception as e:
        status = "Error"
        message = "Error marking task as completed in SFG20"
        response = [{"error": str(e)}]
        print(traceback.format_exc())
    return {"status": status, "message": message, "data": response}


# -------------------------------------------------
# Cache endpoints
# -------------------------------------------------
@app.post(
    "/cache",
    tags=["Cache"],
    response_model=Result,
    description="List the data in the cache according to the parameters provided. When a parameter is ",
    operation_id="get_from_cache",
)
@rate_limited(config.THROTTLE_RATE, config.THROTTLE_TIME)
async def get_from_cache(
    cacheParams: CacheParameters,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
) -> Any:
    status = "OK"
    message = "Data retrieved successfully from SFG20 cache"
    try:
        response = cache.list_cache(cacheParams)
    except Exception as e:
        status = "Error"
        message = "Error retrieving data from SFG20 cache"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": response}


@app.delete(
    "/cache",
    tags=["Cache"],
    response_model=Result,
    description="Delete all the data in the cache for the selected user",
    operation_id="delete_from_cache",
)
@rate_limited(config.THROTTLE_RATE, config.THROTTLE_TIME)
async def delete_from_cache(
    user_id: str,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
) -> Any:
    status = "OK"
    message = f"Successfully cleaned data cache for user {user_id}"
    response = []
    try:
        cache.clear_cache(user_id)
    except Exception as e:
        status = "Error"
        message = "Error cleaning data cache"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": response}


# -------------------------------------------------
# Config endpoints
# -------------------------------------------------
@app.post(
    "/config/add",
    tags=["Config"],
    response_model=Result,
    description="Add a new configuration to the Config table",
    operation_id="config_add",
)
@rate_limited(config.THROTTLE_RATE, config.THROTTLE_TIME)
async def config_add(
    data: Config,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    status = "OK"
    message = "Data saved successfully in Config table"
    try:
        cache.add_config(data)
        response = []
    except Exception as e:
        status = "Error"
        message = "Error saving data in Config table"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": response}


@app.delete(
    "/config/delete/{id}",
    tags=["Config"],
    response_model=Result,
    description="Delete the configuration from the Config table",
    operation_id="config_delete",
)
@rate_limited(config.THROTTLE_RATE, config.THROTTLE_TIME)
async def config_delete(
    id: str,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    status = "OK"
    message = "Data deleted successfully in Config table"
    response = []
    try:
        cache.delete_config(id)
    except Exception as e:
        status = "Error"
        message = "Error deleting data in Config table"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": response}


@app.get(
    "/config/get/{id}",
    tags=["Config"],
    response_model=Result,
    description="Select a configuration from the Config table",
    operation_id="config_select",
)
@rate_limited(config.THROTTLE_RATE, config.THROTTLE_TIME)
async def config_select(
    id: str,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    status = "OK"
    message = "Data retrieved successfully from Config table"
    try:
        response = cache.select_config(id)
    except Exception as e:
        status = "Error"
        message = "Error retrieving data from Config table"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": response}


@app.get(
    "/config/token",
    tags=["Config"],
    response_model=Result,
    description="Delete the configuration from the Config table",
    operation_id="config_select_token",
)
@rate_limited(config.THROTTLE_RATE, config.THROTTLE_TIME)
async def config_select_token(
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    status = "OK"
    message = "Access token retrieved successfully from configuration"
    try:
        raw_response = cache.select_config(str(api_key))
        response = [{"access_token": raw_response[0]["access_token"]}]
    except Exception as e:
        status = "Error"
        message = "Error retrieving data from Config table"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": response}


# -------------------------------------------------
# Shared Links endpoints
# -------------------------------------------------
@app.get(
    "/config/shared_links",
    tags=["Config"],
    response_model=Result,
    description="Get the shared links for the user",
    operation_id="config_select_shared_links",
)
@rate_limited(config.THROTTLE_RATE, config.THROTTLE_TIME)
async def config_shared_links(
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
) -> Any:
    status = "OK"
    message = "Data retrieved successfully from Shared_Links table"
    try:
        response = cache.select_shared_links(str(api_key))
    except Exception as e:
        status = "Error"
        message = "Error retrieving data from Shared_Links table"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": response}


@app.delete(
    "/config/shared_links/{id}",
    tags=["Config"],
    response_model=Result,
    description="Delete a shared link for the user",
    operation_id="config_delete_shared_link",
)
@rate_limited(config.THROTTLE_RATE, config.THROTTLE_TIME)
async def delete_shared_link(
    id: str,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    status = "OK"
    message = "Data deleted successfully in Shared_Links table"
    response = []
    try:
        cache.delete_shared_links(str(api_key), id)
    except Exception as e:
        status = "Error"
        message = "Error deleting data in Shared_Links table"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": response}


@app.post(
    "/config/shared_links",
    tags=["Config"],
    response_model=Result,
    description="Add a new shared link for the user",
    operation_id="config_add_shared_link",
)
@rate_limited(config.THROTTLE_RATE, config.THROTTLE_TIME)
async def add_shared_link(
    data: SharedLinks,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    status = "OK"
    message = "Data saved successfully in Shared_Links table"
    try:
        cache.add_shared_links(data)
        response = []
    except Exception as e:
        status = "Error"
        message = "Error saving data in Shared_Links table"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": response}


# @app.post(
#     "/list/dataverse",
#     tags=["Dataverse"],
#     response_model=Result,
#     description="List the data from the dataverse table, filtered by the key field",
# )
# async def get_list_dataverse(
#     object: Template,
#     api_key: security_router.APIKey = security_router.Depends(
#         security_router.get_api_key
#     ),
# ):
#     status = "OK"
#     message = "Data retrieved successfully from Dataverse"
#     try:
#         session, token = sv_dataverse.getAuthenticatedSession()

#         if session:
#             data = sv_dataverse.retrieve_data(session, object)
#     except Exception as e:
#         status = "Error"
#         message = "Error retrieving data from Dataverse"
#         data = [{"error": str(e)}]
#     return {"status": status, "message": message, "data": data}


# @app.post(
#     "/save/report",
#     tags=["Dataverse"],
#     response_model=Result,
#     description="Save the header information of the report in Dataverse",
# )
# async def post_save_report(
#     report: Report,
#     api_key: security_router.APIKey = security_router.Depends(
#         security_router.get_api_key
#     ),
# ):
#     status = "OK"
#     message = "Data saved successfully in Dataverse report table"
#     try:
#         session, token = sv_dataverse.getAuthenticatedSession()

#         if session:
#             data = sv_dataverse.save_data(
#                 session,
#                 Tables.report,
#                 report.model_dump_json(),
#                 "cr17a_reportuid",
#             )
#     except Exception as e:
#         status = "Error"
#         message = "Error saving data in Dataverse"
#         data = [{"error": str(e)}]
#     return {"status": status, "message": message, "data": [data.json()]}


# @app.post(
#     "/save/task",
#     tags=["Dataverse"],
#     response_model=Result,
#     description="Save the Task information of the report in Dataverse",
# )
# async def post_save_task(
#     task: Task,
#     api_key: security_router.APIKey = security_router.Depends(
#         security_router.get_api_key
#     ),
# ):
#     status = "OK"
#     message = "Data saved successfully in Dataverse task table"
#     try:
#         session, token = sv_dataverse.getAuthenticatedSession()

#         if session:
#             data = sv_dataverse.save_data(
#                 session,
#                 Tables.task,
#                 task.model_dump_json(),
#                 "cr17a_reportuid",
#             )
#     except Exception as e:
#         status = "Error"
#         message = "Error saving data in Dataverse"
#         data = [{"error": str(e)}]
#     return {"status": status, "message": message, "data": [data.json()]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
