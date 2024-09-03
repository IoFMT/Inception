# -*- coding: utf-8 -*-

import libs.config as config
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security.api_key import APIKey, APIKeyCookie, APIKeyHeader, APIKeyQuery
from starlette.responses import JSONResponse, RedirectResponse
from starlette.status import HTTP_403_FORBIDDEN
from libs.utils import encode

API_KEY = config.GLOBAL_API_KEY
API_KEY_NAME = "X-Access-Token"
COOKIE_DOMAIN = "localhost"

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    api_key_cookie: str = Security(api_key_cookie),
):

    if api_key_query and encode(api_key_query) == API_KEY:
        return api_key_query
    elif api_key_header and encode(api_key_header) == API_KEY:
        return api_key_header
    elif api_key_cookie and encode(api_key_cookie) == API_KEY:
        return api_key_cookie
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
