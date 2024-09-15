# -*- coding: utf-8 -*-
"""
    Main file to run the API
"""
import json
from time import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi


from routers import security_router
from entities.search import SearchTerm, Entities
from entities.template import Template

from services import dataverse as sv_dataverse
from services import sfg20 as sv_sfg20


app = FastAPI(title="IoFMT REST API")

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="IoFMT REST API",
        version="0.2.0",
        summary="This is a rest API for the IoFMT project",
        description="This is a rest API for the IoFMT project",
        routes=app.routes,
        openapi_version="3.0.2",
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.middleware("http")
async def time_call(request: Request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time()
    response.headers["X-Process-Time"] = str(process_time - start_time)
    return response


@app.get("/", tags=["Version 1"])
async def get_root():
    return {"Status": "OK"}


@app.post("/search", tags=["Version 1"])
async def get_search(
    search: SearchTerm,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    response = sv_sfg20.retrieve_data()
    return response


@app.get("/list/cache", tags=["Version 1"])
async def list_cache(
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    response = sv_sfg20.list_data()
    return response


@app.get("/retrieve/{type_id}", tags=["Version 1"])
async def get_retrieve_template(
    type_id: Entities,
    schedule_id: str,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    if type_id == Entities.all:
        response = sv_sfg20.list_data(schedule_id)
    else:
        response = sv_sfg20.list_data(schedule_id, type_id)
    return {"data": response}


@app.get("/list", tags=["Version 1"])
async def get_list_dataverse(
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    session, token = sv_dataverse.getAuthenticatedSession()

    if session:
        data = sv_dataverse.retrieve_data(session, token)

    return {"data": data}


@app.post("/save", tags=["Version 1"])
async def post_save_template(
    template: Template,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    session, token = sv_dataverse.getAuthenticatedSession()

    if session:
        data = sv_dataverse.save_data(session, token, template.model_dump_json())
    return {"Template": data}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# TODO: add description to the endpoints

# TODO: add tags to the endpoints

# TODO: review the endpoints needed and create the new ones
