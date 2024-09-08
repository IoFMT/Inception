# Deploying Python API to Azure App Service

This document describes how to deploy a Python API to Azure App Service via Github Actions.

## Prerequisites

- Azure CLI
- That you have installed the app manually first. To do that, follow the steps in the [manual-deployment.md](manual-deployment.md) document.
- the subscriptionId of your Azure App Service


## Steps to Configure Github Actions

### 1. Generate Deployment Credentials

a) Create a service application

```bash
az ad app create --display-name inceptionapi
```

From the json output, collect the appId and the objectId (id).

b) Create a service principal

```bash
az ad sp create --id <appId>
```

From the json output, collect the assigneeObjectId (id) and appOwnerOrganizationId.

c) Create a new role assignment

```bash
az role assignment create --role contributor --subscription <subscriptionId> --assignee-object-id  <assigneObjectId> --scope /subscriptions/<subscriptionId>/resourceGroups/inception-api-rg/providers/Microsoft.Web/sites/iofmtapi --assignee-principal-type ServicePrincipal
```

d) Create a new federated identity credential

First you need to creata a credential.json file

```json
{
  "name": "iofmtapi-cr",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:IoFMT/Inception:ref:refs/heads/main",
  "description": "Testing",
  "audiences": [
    "api://AzureADTokenExchange"
  ]
}
```

Then execute the command:

```bash
az ad app federated-credential create --id <subscriptionId> --parameters credential.json  
```

### 2) Configure GitHub Secrets

Add the following to your Github Secrets on your repository:

| Variable | Meaning |
|--------------|-----------------------|
| AZURE_CLIENT_ID | Application (client) ID |
| AZURE_TENANT_ID |	Directory (tenant) ID |
| AZURE_SUBSCRIPTION_ID |	Subscription ID |

