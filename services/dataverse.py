import os
import logging

import msal
import requests

from libs import config


logging.basicConfig(level=logging.DEBUG)


def getAuthenticatedSession():

    token_cache = msal.SerializableTokenCache()

    if os.path.exists(config.CACHEFILE):
        logging.info("Loading cache file")
        token_cache.deserialize(open(config.CACHEFILE, "r").read())

    app = msal.PublicClientApplication(
        config.CLIENT_ID, authority=config.AUTHORITY, token_cache=token_cache
    )

    result = None

    accounts = app.get_accounts()
    print(accounts)

    if len(accounts) == 0:
        logging.warning("No accounts found, please sign in.")
        logging.info(
            "A local browser window will open for you to sign in. CTRL+C to cancel."
        )
        result = app.acquire_token_interactive(config.SCOPE)
    else:
        result = app.acquire_token_silent(config.SCOPE, account=accounts[0])

    if "access_token" in result:
        logging.info("Token received successfully")
        session = requests.Session()
        session.headers.update(
            dict(Authorization="Bearer {}".format(result["access_token"]))
        )
        session.headers.update(
            {
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0",
                "If-None-Match": "null",
                "Accept": "application/json",
            }
        )
        return session, token_cache
    else:
        logging.error(result("error"))
        logging.error(result("error_description"))
        logging.error(result("correlation_id"))
        return None, None


def retrieve_data(session, token_cache):
    graph_data = session.get(  # Use token to call downstream service
        f"{config.WEB_API_URL}api/data/v9.2/{config.DV_SELECTED_TABLE}?$select={','.join(config.DV_SELECTED_FIELDS)}"
    ).json()

    results = graph_data.get("value", [])
    return results


def save_data(session, token_cache, data):
    graph_data = session.post(
        f"{config.WEB_API_URL}api/data/v9.2/{config.DV_SELECTED_TABLE}",
        json=data,
    )

    return graph_data
