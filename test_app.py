import pytest
from fastapi.testclient import TestClient
from app import app
from routers.security_router import APIKey, get_api_key

client = TestClient(app)
header = {"X-Access-Token": "iofmt2024@"}


# Mock the get_api_key dependency
# def override_get_api_key():
#     return APIKey(key="X-Access-Token")


# app.dependency_overrides[get_api_key] = override_get_api_key


def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Status": "OK"}


def test_get_search():
    search_term = {"term": "example"}
    response = client.post("/search", json=search_term, headers=header)
    assert response.status_code == 200
    assert response.json() == search_term


def test_get_retrieve_template():
    template_id = "123"
    response = client.get(f"/retrieve/{template_id}", headers=header)
    assert response.status_code == 200
    assert response.json() == {"TemplateID": template_id}


def test_get_list_dataverse(mocker):
    mocker.patch(
        "services.dataverse.getAuthenticatedSession", return_value=(True, "token")
    )
    mocker.patch(
        "services.dataverse.retrieve_data", return_value={"data": "example_data"}
    )

    response = client.get("/list", headers=header)
    assert response.status_code == 200
    assert response.json() == {"data": {"data": "example_data"}}


def test_post_save_template(mocker):
    template = {"cr17a_id": "2", "cr17a_name": "example_template"}
    mocker.patch(
        "services.dataverse.getAuthenticatedSession", return_value=(True, "token")
    )
    mocker.patch("services.dataverse.save_data", return_value=template)

    response = client.post("/save", json=template, headers=header)
    assert response.status_code == 200
    assert response.json() == {"Template": template}
