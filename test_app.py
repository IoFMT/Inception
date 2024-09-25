import pytest
from fastapi.testclient import TestClient
from app import app
from routers.security_router import APIKey, get_api_key

client = TestClient(app)
header = {"X-Access-Token": "iofmt2024@"}


def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "message": "IoFMT REST API is running",
        "data": [{"version": "1.0.0"}],
    }


def test_config_add():
    config_data = {
        "api_key": "test_key",
        "customer_name": "test_customer",
        "access_token": "test_token",
    }
    response = client.post("/config/add", json=config_data, headers=header)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


def test_config_select():
    response = client.get("/config/get/test_key", headers=header)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"
    assert response.json()["data"][0]["api_key"] == "test_key"
    assert response.json()["data"][0]["customer_name"] == "test_customer"
    assert response.json()["data"][0]["access_token"] == "test_token"


def test_add_shared_link():
    shared_link_data = {
        "api_key": "test_key",
        "id": "test_id",
        "link_name": "test_link",
        "url": "test_url",
    }
    response = client.post(
        "/config/shared_links", json=shared_link_data, headers=header
    )
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


def test_get_shared_links():
    header2 = {"X-Access-Token": "test_key"}
    response = client.get("/shared-links", headers=header2)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"
    assert response.json()["data"][0]["id"] == "test_id"
    assert response.json()["data"][0]["name"] == "test_link"
    assert response.json()["data"][0]["url"] == "test_url"


def test_get_shared_links_config():
    header2 = {"X-Access-Token": "test_key"}
    response = client.get("/config/shared_links", headers=header2)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"
    assert response.json()["data"][0]["id"] == "test_id"


def test_delete_shared_link():
    header2 = {"X-Access-Token": "test_key"}
    response = client.delete("/config/shared_links/test_id", headers=header2)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


def test_config_select_token():
    header2 = {"X-Access-Token": "test_key"}
    response = client.get("/config/token", headers=header2)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"
    assert response.json()["data"][0]["access_token"] == "test_token"


def test_config_delete():
    header2 = {"X-Access-Token": "test_key"}
    response = client.delete("/config/delete/test_key", headers=header)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


"""
def test_get_schedules():
    search_term = {"term": "test"}
    response = client.post("/schedules", json=search_term, headers=header)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


def test_get_from_cache():
    cache_params = {"param": "test"}
    response = client.post("/cache", json=cache_params, headers=header)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


def test_delete_from_cache():
    response = client.delete("/cache", params={"user_id": "test_user"}, headers=header)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"

"""
