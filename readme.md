# IoFMT REST API

This repository contains a REST API built with FastAPI for the IoFMT project. The API provides endpoints for searching, retrieving, listing, and saving data related to SFG20 templates.


## Technologies

* **FastAPI:** A modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
* **Uvicorn:** An ASGI web server implementation for Python.
* **PostgreSQL:** A database for caching information.
* **SFG20 GraphQL:** The GraphQL API for accessing SFG20 data.


## Requirements

* Python 3.7+

## Installation

1. Clone the repository:

```
git clone https://github.com/your-username/iofmt-api.git
cd iofmt-api
```

2. Create and activate a virtual environment (recommended):

```
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

## Configuration

1. Create a .env file in the root directory and add the following environment variables:

```
GLOBAL_API_KEY="<APIKEY>"
DV_CLIENT_ID="<AZURE SERVICE ACCOUNT>"
DV_TENANT_ID="<AZURE TENANT>"
DV_BASE_URL="https://orgf03f2423.crm11.dynamics.com/"
DV_AUTH_BASE="https://login.microsoftonline.com/"
DV_SCP_SUFFIX="user_impersonation"
DV_CLIENT_SECRET="<SA CLIENT SECRET>"
DV_CLIENT_SECRETID = "<SA CLIENT SECRET ID>"
DV_CACHE_FILE = "services/cache/cache.bin"

CACHE_DB_HOST="<PostgreSQL Host>"
CACHE_DB_USER="<PostgreSQL user>"
CACHE_DB_PWD="<PostgreSQL pwd>"

ADMIN_USER = "<API admin user>"
ADMIN_PWD = "<API admin pwd>"

AZURE_CLIENT_ID="<AZURE CLIENT ID>"
AZURE_TENANT_ID="<AZURE TENANT ID>"
APPLICATION-OBJECT-ID="<APP SERVICE ID>"
ASSIGNEE-OBJECT-ID="<ASSIGNEE OBJECT ID>"
SUBSCRIPTION_ID="<SUBSCRIPTION ID>"

DEMO_SFG20_URL="https://api.demo.facilities-iq.com/v3.0"
PROD_SFG20_URL="https://api.facilities-iq.com/v3.0"
```

2. Set up API Key:
    * Using the generate_apikey.py generate a new Master API key
    *  Save your encripted API key on the .env file. 

3. Create the PostgreSQL tables:

Execute the scripts available at the data folder, in no particular order, using the connection information that you collect for the environment variables.


4. Create the cache file:

## Running the API

1. Start the Uvicorn server:

```
uvicorn main:app --reload
```

2. Access the API documentation at http://localhost:8000/docs.


## Authentication

All endpoints require an API key for authentication. You need to include your API key in the request header as `X-Access-Token`.


## Preparing to deploy on Azure

Check the 2 guides below:

1) [Deploy Manually to Azure App Service](manual-deployment.md)
2) [Deploy using GitHub Actions](automated-deployment.md)


## Understanding the API

This document provides a technical overview of the IOFMT REST API.

**API Specification:**

The API is defined using the OpenAPI Specification (OAS) and can be accessed at `https://iofmtapi.azurewebsites.net/openapi.json`. This API definition is using OPENAPI 3.0.3.
If you want a version using swagger 2, please open this file: [Swagger 2 Definition](connector/IoFMT-API.swagger.json)

**Authentication:**

The API uses API Key authentication. You can obtain an API Key by visiting the [Admin](https://iofmtapi.azurewebsites.net/admin) page.

**Endpoints:**

**1. `/`**

* **GET:** Retrieves API status.

    * **Tags:** `Basic`
    * **Summary:** Get Api Status
    * **Response:**
        * **200 OK:** Returns API status as a `Result` object. The `Result` object contains the following properties:
            * `status`: The status of the request.
            * `message`: The message of the request.
            * `data`: The data of the request.

    * **Produces:** `application/json`

**2. `/schedules`**

* **POST:** Retrieves schedules from SFG20 and loads them into the cache.

    * **Tags:** `SFG20`
    * **Summary:** Get Schedules
    * **Description:** Search SFG20 schedules according to the parameters provided and load into the cache.
    * **Response:**
        * **200 OK:** Returns a `Result` object containing retrieved schedules.
        * **422 Unprocessable Entity:** Validation error in request body. Returns a `HTTPValidationError` object.

    * **Security:** API Key required.
    * **Parameters:**
        * `body`: (Required) `SearchTerm` object containing the search criteria.
    * **Consumes:** `application/json`
    * **Produces:** `application/json`

**3. `/shared-links`**

* **GET:** Retrieves a list of available SFG20 shared links for the authenticated user.

    * **Tags:** `SFG20`
    * **Summary:** Get Shared Links
    * **Description:** List the SFG20 shared links available for the user.
    * **Response:**
        * **200 OK:** Returns a `Result` object containing a list of shared links.

    * **Security:** API Key required.
    * **Produces:** `application/json`

**4. `/task/complete`**

* **POST:** Marks a task as completed in SFG20.

    * **Tags:** `SFG20`
    * **Summary:** Complete Task
    * **Description:** Mark a task as completed in SFG20.
    * **Response:**
        * **200 OK:** Returns a `Result` object indicating success.
        * **422 Unprocessable Entity:** Validation error in request body. Returns a `HTTPValidationError` object.

    * **Security:** API Key required.
    * **Parameters:**
        * `body`: (Required) `Task` object containing the task details to mark as completed.
    * **Consumes:** `application/json`
    * **Produces:** `application/json`

**5. `/task_group/complete`**

* **POST:** Marks a group of tasks as completed in SFG20.

    * **Tags:** `SFG20`
    * **Summary:** Complete Task Group
    * **Description:** Mark a group of tasks as completed in SFG20.
    * **Response:**
        * **200 OK:** Returns a `Result` object indicating success.
        * **422 Unprocessable Entity:** Validation error in request body. Returns a `HTTPValidationError` object.

    * **Security:** API Key required.
    * **Parameters:**
        * `body`: (Required) `TaskGroup` object containing the task group details to mark as completed.
    * **Consumes:** `application/json`
    * **Produces:** `application/json`

**6. `/cache`**

* **POST:** Retrieves data from the cache based on provided parameters.

    * **Tags:** `Cache`
    * **Summary:** Get From Cache
    * **Description:** List the data in the cache according to the parameters provided.
    * **Response:**
        * **200 OK:** Returns a `Result` object containing the requested data.
        * **422 Unprocessable Entity:** Validation error in request body. Returns a `HTTPValidationError` object.

    * **Security:** API Key required.
    * **Parameters:**
        * `body`: (Required) `CacheParameters` object containing the cache retrieval criteria.
    * **Consumes:** `application/json`
    * **Produces:** `application/json`

* **DELETE:** Deletes all data from the cache for the specified user.

    * **Tags:** `Cache`
    * **Summary:** Delete From Cache
    * **Description:** Delete all the data in the cache for the selected user.
    * **Response:**
        * **200 OK:** Returns a `Result` object indicating success.
        * **422 Unprocessable Entity:** Validation error in request parameters. Returns a `HTTPValidationError` object.

    * **Security:** API Key required.
    * **Parameters:**
        * `user_id`: (Required) The ID of the user to delete cache data for.
    * **Produces:** `application/json`

**7. `/config/add`**

* **POST:** Adds a new configuration to the Config table.

    * **Tags:** `Config`
    * **Summary:** Config Add
    * **Description:** Add a new configuration to the Config table.
    * **Response:**
        * **200 OK:** Returns a `Result` object indicating success.
        * **422 Unprocessable Entity:** Validation error in request body. Returns a `HTTPValidationError` object.

    * **Security:** API Key required.
    * **Parameters:**
        * `body`: (Required) `Config` object containing the configuration details to add.
    * **Consumes:** `application/json`
    * **Produces:** `application/json`

**8. `/config/delete/{id}`**

* **DELETE:** Deletes a configuration from the Config table.

    * **Tags:** `Config`
    * **Summary:** Config Delete
    * **Description:** Delete the configuration from the Config table.
    * **Response:**
        * **200 OK:** Returns a `Result` object indicating success.
        * **422 Unprocessable Entity:** Validation error in request parameters. Returns a `HTTPValidationError` object.

    * **Security:** API Key required.
    * **Parameters:**
        * `id`: (Required) The ID of the configuration to delete.
    * **Produces:** `application/json`

**9. `/config/get/{id}`**

* **GET:** Retrieves a configuration from the Config table.

    * **Tags:** `Config`
    * **Summary:** Config Select
    * **Description:** Select a configuration from the Config table.
    * **Response:**
        * **200 OK:** Returns a `Result` object containing the requested configuration.
        * **422 Unprocessable Entity:** Validation error in request parameters. Returns a `HTTPValidationError` object.

    * **Security:** API Key required.
    * **Parameters:**
        * `id`: (Required) The ID of the configuration to retrieve.
    * **Produces:** `application/json`

**10. `/config/token`**

* **GET:** Retrieves the token from the Config table.

    * **Tags:** `Config`
    * **Summary:** Config Select Token
    * **Description:** Delete the configuration from the Config table.
    * **Response:**
        * **200 OK:** Returns a `Result` object containing the token.

    * **Security:** API Key required.
    * **Produces:** `application/json`

**11. `/config/shared_links`**

* **GET:** Retrieves the shared links for the authenticated user.

    * **Tags:** `Config`
    * **Summary:** Config Shared Links
    * **Description:** Get the shared links for the user.
    * **Response:**
        * **200 OK:** Returns a `Result` object containing the shared links.

    * **Security:** API Key required.
    * **Produces:** `application/json`

* **POST:** Adds a new shared link for the authenticated user.

    * **Tags:** `Config`
    * **Summary:** Add Shared Link
    * **Description:** Add a new shared link for the user.
    * **Response:**
        * **200 OK:** Returns a `Result` object indicating success.
        * **422 Unprocessable Entity:** Validation error in request body. Returns a `HTTPValidationError` object.

    * **Security:** API Key required.
    * **Parameters:**
        * `body`: (Required) `SharedLinks` object containing the shared link details to add.
    * **Consumes:** `application/json`
    * **Produces:** `application/json`

**12. `/config/shared_links/{id}`**

* **DELETE:** Deletes a shared link for the authenticated user.

    * **Tags:** `Config`
    * **Summary:** Delete Shared Link
    * **Description:** Delete a shared link for the user.
    * **Response:**
        * **200 OK:** Returns a `Result` object indicating success.
        * **422 Unprocessable Entity:** Validation error in request parameters. Returns a `HTTPValidationError` object.

    * **Security:** API Key required.
    * **Parameters:**
        * `id`: (Required) The ID of the shared link to delete.
    * **Produces:** `application/json`

**Error Handling:**

The API uses standard HTTP status codes to indicate success or error conditions.

* **2xx:** Success.
* **4xx:** Client error.
* **5xx:** Server error.

**Definitions:**

The API uses the following definitions:

* **CacheParameters:** Object containing parameters for retrieving data from the cache.
* **Config:** Object containing configuration details.
* **Entities:** Enumeration of entities supported in the API.
* **HTTPValidationError:** Object representing validation errors.
* **Result:** Object containing the result of an API request.
* **SearchTerm:** Object containing search criteria for retrieving schedules.
* **SharedLinks:** Object containing shared link details.
* **Task:** Object containing task details.
* **TaskGroup:** Object containing task group details.
* **TaskGroupItem:** Object containing individual task details within a task group.
* **ValidationError:** Object representing an individual validation error.

**Security:**

The API uses the following security definitions:

* **APIKeyQuery:** API Key passed as a query parameter.
* **APIKeyHeader:** API Key passed as a header.
* **APIKeyCookie:** API Key passed as a cookie.


This documentation provides a comprehensive overview of the IOFMT REST API. For detailed information on each endpoint, including request and response schemas, please refer to the API specification available at `https://iofmtapi.azurewebsites.net/openapi.json`.
