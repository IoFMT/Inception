# -*- coding: utf-8 -*-
"""
    Main file to run the API
"""
import json
from time import time
import traceback
import requests

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi


from routers import security_router
from entities.sfg20 import CacheParameters, SearchTerm, Entities
from entities.template import Template
from entities.base import Result
from typing import Any


from services import dataverse as sv_dataverse
from services import sfg20 as sv_sfg20


app = FastAPI(title="IoFMT REST API")


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
        version="0.3.0",
        summary="This is a REST API for IoFMT project",
        description="This REST API acts as a Facade for connecting to the differemt data sources: SFG20 and Dataverse. This API is also mapped in a Power Platform Custom Connector.",
        routes=app.routes,
        openapi_version="3.0.2",
        tags=sv_sfg20.config.tags_metadata,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# -------------------------------------------------
# Endpoints
# -------------------------------------------------


@app.get("/", tags=["Basic"], response_model=Result)
async def get_root() -> Any:
    return {
        "status": "OK",
        "message": "IoFMT REST API is running",
        "data": [{"version": "0.3.0"}],
    }


@app.post(
    "/search",
    tags=["SFG20"],
    response_model=Result,
    description="Search SFG20 schedules according to the parameters provided and load into the cache",
)
async def get_search(
    search: SearchTerm,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
) -> Any:
    status = "OK"
    message = "Data retrieved successfully from SFG20 and cached in the API"
    try:
        response = sv_sfg20.retrieve_all_data(search)
    except Exception as e:
        status = "Error"
        message = "Error retrieving data from SFG20"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": response}


@app.post(
    "/list/cache",
    tags=["SFG20"],
    response_model=Result,
    description="List the data in the cache according to the parameters provided",
)
async def list_cache(
    cacheParams: CacheParameters,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
) -> Any:
    status = "OK"
    message = "Data retrieved successfully from SFG20 cache"
    try:
        response = sv_sfg20.list_data(cacheParams)
    except Exception as e:
        status = "Error"
        message = "Error retrieving data from SFG20 cache"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": response}


@app.get(
    "/list/links",
    tags=["SFG20"],
    response_model=Result,
    description="List the data in the cache according to the parameters provided",
)
async def get_list_links(
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
) -> Any:
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

    return {
        "status": "OK",
        "message": "List of SFG20 shared links",
        "data": data,
    }


@app.get(
    "/delete/cache",
    tags=["SFG20"],
    response_model=Result,
    description="Delete all the data in the cache for the informed user",
)
async def list_cache(
    user_id: str,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
) -> Any:
    status = "OK"
    message = "Successfully Cleaning SFG20 cache"
    try:
        response = sv_sfg20.clear_data(user_id)
    except Exception as e:
        status = "Error"
        message = "Error cleaning SFG20 cache"
        response = [{"error": str(e)}]
    return {"status": status, "message": message, "data": response}


@app.get(
    "/list/dataverse",
    tags=["Dataverse"],
    response_model=Result,
    description="List the data in the Dataverse",
)
async def get_list_dataverse(
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    status = "OK"
    message = "Data retrieved successfully from Dataverse"
    try:
        session, token = sv_dataverse.getAuthenticatedSession()

        if session:
            data = sv_dataverse.retrieve_data(session, token)
    except Exception as e:
        status = "Error"
        message = "Error retrieving data from Dataverse"
        data = [{"error": str(e)}]
    return {"status": status, "message": message, "data": data}


@app.post(
    "/save",
    tags=["Dataverse"],
    response_model=Result,
    description="Save the template in the Dataverse",
)
async def post_save_template(
    template: Template,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    status = "OK"
    message = "Data retrieved successfully from SFG20 cache"
    try:
        session, token = sv_dataverse.getAuthenticatedSession()

        if session:
            data = sv_dataverse.save_data(session, token, template.model_dump_json())
    except Exception as e:
        status = "Error"
        message = "Error saving data in Dataverse"
        data = [{"error": str(e)}]
    return {"status": status, "message": message, "data": data}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# TODO: review the endpoints needed and create the new ones
