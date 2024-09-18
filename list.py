# -*- coding: utf-8 -*-
"""
  Generate a token for the dataverse api
"""

import json
import requests
from services import dataverse as sv_dataverse
from libs import config

# session, token = sv_dataverse.getAuthenticatedSession()

# if token:
#     response = session.get("https://graph.microsoft.com/v1.0/sites")
#     print(json.dumps(response.json(), indent=2))

url = "https://api.demo.facilities-iq.com/graphql?o=GetMyShareLinks"

headers = {
    "accept": "*/*",
    "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "clientid": "JiBG2T2dqSuh9B:sfg20/clients",
    "content-type": "application/json",
    "href": "https://www.demo.facilities-iq.com/app",
    "instance": "kvhCEofyDSRF87",
    "priority": "u=1, i",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "cookie": "_ga=GA1.1.551238647.1726408191; _ga_ZESBZLG4GM=GS1.1.1726485952.3.1.1726486310.59.0.0; token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IndhbHRlckBpb2ZtdG1zLmNvbSIsImlhdCI6MTcyNjQ4NjMxMCwiZXhwIjoxNzI3MDkxMTEwfQ.j9NPmWt9-QCb0KIoTwzMkfXAQHP4RihI-7ahCZJjA6g",
    "Referer": "https://www.demo.facilities-iq.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

payload = '[{"operationName":"GetMyShareLinks","variables":{"search":""},"query":"query GetMyShareLinks($search: String, $take: Int, $skip: Int) {  getMyShareLinks(skip: $skip, take: $take, search: $search) {    total    links {      client      creator      endDate      name      outOfDate      startDate      url      when      __typename    }    outOfDateLinks    __typename  }}"}]'

response = requests.post(url, headers=headers, data=payload)

print(response.json())
