import os

import msal
import requests

from libs import config


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
                "Content-Type": "application/json; charset=utf-8",
                "Prefer": "return=representation",
            }
        )
        return session, token_cache
    else:
        logging.error(result("error"))
        logging.error(result("error_description"))
        logging.error(result("correlation_id"))
        return None, None


def retrieve_data(session, object):
    graph_data = session.get(  # Use token to call downstream service
        f"{config.WEB_API_URL}api/data/v9.2/{object.table_name}?$filter={object.key_field} eq '{object.key_value}'",
    ).json()

    print(graph_data)
    results = graph_data.get("value", [])
    return results


def save_data(session, table_name, data, key_field):
    graph_data = session.post(
        f"{config.WEB_API_URL}api/data/v9.2/{table_name}?$select={key_field}",
        json=data,
    )
    return graph_data
