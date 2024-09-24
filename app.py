# -*- coding: utf-8 -*-
"""
    Main file to run the API
"""
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
from entities.sfg20 import CacheParameters, SearchTerm
from entities.base import Config, Result
from services import sfg20 as sv_sfg20
from services import cache
from libs import config
from libs.utils import decode

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
        version="0.5.0",
        summary="This is a REST API for IoFMT Inception project",
        description="""This REST API acts as a Facade for connecting to SFG20 GraphAPI and maintain a cache to expedite performance.
        <br><br>
        This API is also mapped in a Power Platform Custom Connector.
        <br><br>
        To generate the API KEY for a customer, please go to: <a href='https://iofmtapi.azurewebsites.net/admin' target='_blank'>Admin</a>""",
        routes=app.routes,
        openapi_version="3.0.2",
        tags=sv_sfg20.config.tags_metadata,
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
@app.get("/", tags=["Basic"], response_model=Result)
async def get_api_status() -> Any:
    return {
        "status": "OK",
        "message": "IoFMT REST API is running",
        "data": [{"version": "0.3.0"}],
    }


@app.get("/admin", tags=["Basic"], response_class=HTMLResponse, include_in_schema=False)
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


@app.post(
    "/search",
    tags=["SFG20"],
    response_model=Result,
    description="Search SFG20 schedules according to the parameters provided and load into the cache",
)
async def get_schedules(
    search: SearchTerm,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
) -> Any:
    status = "OK"
    message = "Data retrieved successfully from SFG20 and cached in the API"
    try:
        raw_data = sv_sfg20.retrieve_all_data(search)
        response = []
        for item in raw_data:
            cache.save_cache(item)
            response.append(item["schedule"][0])
    except Exception as e:
        status = "Error"
        message = "Error retrieving data from SFG20"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": response}


@app.get(
    "/list/links",
    tags=["SFG20"],
    response_model=Result,
    description="List the SFG20 shared links available for the user",
)
async def get_list_links(
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
) -> Any:
    if api_key == config.GLOBAL_API_KEY:
        url = "https://api.demo.facilities-iq.com/graphql?o=GetMyShareLinks"

        headers = {
            "accept": "*/*",
            "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "clientid": "JiBG2T2dqSuh9B:sfg20/clients",
            "content-type": "application/json",
            "href": "https://www.demo.facilities-iq.com/app",
            "instance": "kvhCEofyDSRF87",
            "priority": "u=1, i",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "cookie": "_ga=GA1.1.551238647.1726408191; _ga_ZESBZLG4GM=GS1.1.1726485952.3.1.1726486310.59.0.0; token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IndhbHRlckBpb2ZtdG1zLmNvbSIsImlhdCI6MTcyNjQ4NjMxMCwiZXhwIjoxNzI3MDkxMTEwfQ.j9NPmWt9-QCb0KIoTwzMkfXAQHP4RihI-7ahCZJjA6g",
            "Referer": "https://www.demo.facilities-iq.com/",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }

        payload = '[{"operationName":"GetMyShareLinks","variables":{"search":""},"query":"query GetMyShareLinks($search: String, $take: Int, $skip: Int) {  getMyShareLinks(skip: $skip, take: $take, search: $search) {    total    links {    name      url    }    outOfDateLinks    __typename  }}"}]'

        response = requests.post(url, headers=headers, data=payload)
        raw_data = response.json()[0]["data"]["getMyShareLinks"]["links"]
        data = []
        for item in raw_data:
            record = {
                "id": item["url"].split("=")[1],
                "name": item["name"],
                "url": item["url"],
            }
            data.append(record)
    else:
        response = cache.select_config(api_key)
        data = response[0]["shared_links"]

    return {
        "status": "OK",
        "message": "List of SFG20 shared links",
        "data": data,
    }


@app.post(
    "/list/cache",
    tags=["Cache"],
    response_model=Result,
    description="List the data in the cache according to the parameters provided. When a parameter is ",
)
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


@app.get(
    "/delete/cache",
    tags=["Cache"],
    response_model=Result,
    description="Delete all the data in the cache for the selected user",
)
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


@app.post(
    "/config/add",
    tags=["Config"],
    response_model=Result,
    description="Add a new configuration to the Config table",
)
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


@app.get(
    "/config/delete/{id}",
    tags=["Config"],
    response_model=Result,
    description="Delete the configuration from the Config table",
)
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
    description="Delete the configuration from the Config table",
)
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
)
def config_select_token(
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


# TODO: two endpoints for saving data in SFG20

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
