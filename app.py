# -*- coding: utf-8 -*-
"""
    Main file to run the API
"""
from time import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


from routers import security_router
from entities.search import SearchTerm
from entities.template import Template


app = FastAPI(title="IOFMT REST API")

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
    return search


@app.get("/retrieve/{template_id}", tags=["Version 1"])
async def get_retrieve_template(
    template_id: str,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    return {"TemplateID": template_id}


@app.post("/save", tags=["Version 1"])
async def post_save_template(
    template: Template,
    api_key: security_router.APIKey = security_router.Depends(
        security_router.get_api_key
    ),
):
    return {"TemplateID": json.load(template)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
