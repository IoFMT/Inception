# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security.api_key import APIKey, APIKeyCookie, APIKeyHeader, APIKeyQuery
from starlette.responses import JSONResponse, RedirectResponse
from starlette.status import HTTP_403_FORBIDDEN

import libs.config as config
from libs.utils import encode
from services import cache

API_KEY = None
API_KEY_NAME = "X-Access-Token"
COOKIE_DOMAIN = "localhost"

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)


def retrieve_api_key(api_key: str):
    if encode(api_key) == config.GLOBAL_API_KEY:
        return api_key
    else:
        results = cache.select_config(api_key)
        return results


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    api_key_cookie: str = Security(api_key_cookie),
):
    if api_key_query:
        results = retrieve_api_key(api_key_query)
        if results:
            return api_key_query
        else:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
            )
    elif api_key_header:
        results = retrieve_api_key(api_key_header)
        if results:
            return api_key_header
        else:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
            )
    elif api_key_cookie:
        results = retrieve_api_key(api_key_cookie)
        if results:
            return api_key_cookie
        else:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
            )
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
