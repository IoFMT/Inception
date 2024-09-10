# IoFMT REST API

This repository contains a REST API built with FastAPI for the IoFMT project. The API provides endpoints for searching, retrieving, listing, and saving data related to SFG20 templates.


## Technologies

* **FastAPI:** A modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
* **Uvicorn:** An ASGI web server implementation for Python.
* **Dataverse:** MS data repository.


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
```

2. Set up API Key:
    * Using the generate_apikey.py generate a new API key
    *  Save your encripted API key on the .env file. 

3. Dataverse Integration:
    * Create a service account on Azure Active Directory
    * Add the service account to the Dataverse environment
    * Save the service account credentials on the .env file
    
    <!-- TODO: Add more detailed instructions -->

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