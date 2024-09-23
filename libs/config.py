# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# Initialize the variables

GLOBAL_API_KEY = None
WEB_API_URL = None
SCOPE = None
CLIENT_ID = None
AUTHORITY = None
CACHEFILE = None
SFG20_ACCESS_TOKEN = None
SFG20_SHARE_ID = None
SFG20_URL = None

# Load the environment variables
load_dotenv()

# Set the variables from the environment
if "GLOBAL_API_KEY" in os.environ:
    GLOBAL_API_KEY = os.environ["GLOBAL_API_KEY"]

# -------------------------------------------------
# Cache DB configuration
# -------------------------------------------------
if "CACHE_DB_HOST" in os.environ:
    CACHE_DB_HOST = os.environ["CACHE_DB_HOST"]

if "CACHE_DB_USER" in os.environ:
    CACHE_DB_USER = os.environ["CACHE_DB_USER"]

if "CACHE_DB_PWD" in os.environ:
    CACHE_DB_PWD = os.environ["CACHE_DB_PWD"]

# CACHE_DB = "data/cache.db"
CACHE_DB = f"postgresql://{CACHE_DB_USER}:{CACHE_DB_PWD}@{CACHE_DB_HOST}/postgres"

CACHE_DB_FIELDS = {
    "schedules": ["id", "code", "title", "rawTitle", "modified", "version"],
    "skills": ["skill.CoreSkillingID", "skill.Skilling", "skill.SkillingCode"],
    "tasks": [
        "id",
        "title",
        "classification",
        "frequency.interval",
        "frequency.period",
        "minutes",
        "date",
        "url",
        "linkId",
        "content",
        "fullContent",
        "fullHtmlContent",
        "skill.CoreSkillingID",
        "skill.Skilling",
        "schedule.code",
        "schedule.version",
        "steps",
    ],
    "assets": ["id", "description"],
    "frequencies": ["label", "label"],
    "classification": ["classification", "classification"],
}

CACHE_SQL_CREATE = """CREATE TABLE IF NOT EXISTS public.sfg20_data (user_id TEXT, 
                                                            sharelink_id TEXT, 
                                                            schedule_id TEXT, 
                                                            type TEXT, 
                                                            data TEXT)"""
CACHE_SQL_DELETE = """DELETE FROM public.sfg20_data WHERE user_id = :p1 and sharelink_id = :p2 and schedule_id = :p3"""

CACHE_SQL_INSERT = """INSERT INTO public.sfg20_data (user_id, sharelink_id, schedule_id, type, data) VALUES (:p1, :p2, :p3, :p4, :p5)"""

CACHE_SQL_CLEAR = """DELETE FROM public.sfg20_data WHERE user = :p1"""

CACHE_SQL_INSERT_CONFIG = """INSERT INTO public.config (api_key, customer_name, access_token, shared_links) VALUES (:p1, :p2, :p3, :p4)"""

CACHE_SQL_DELETE_CONFIG = """DELETE FROM public.config WHERE api_key = :p1"""


# -------------------------------------------------
# Dataverse Configuration
# -------------------------------------------------
if "DV_BASE_URL" in os.environ:
    WEB_API_URL = os.environ["DV_BASE_URL"]

if WEB_API_URL and "DV_SCP_SUFFIX" in os.environ:
    SCOPE = [WEB_API_URL + "/" + os.environ.get("DV_SCP_SUFFIX")]

if "DV_CLIENT_ID" in os.environ:
    CLIENT_ID = os.environ.get("DV_CLIENT_ID")

if "DV_AUTH_BASE" in os.environ and "DV_TENANT_ID" in os.environ:
    AUTHORITY = os.environ.get("DV_AUTH_BASE") + os.environ.get("DV_TENANT_ID")

if "DV_CACHE_FILE" in os.environ:
    CACHEFILE = os.environ.get("DV_CACHE_FILE")

DV_SELECTED_TABLE = "cr17a_test_tbls"
DV_SELECTED_FIELDS = ["cr17a_id", "cr17a_name"]

# -------------------------------------------------
# SFG20 GraphSQL Queries
# -------------------------------------------------
if "SFG20_ACCESS_TOKEN" in os.environ:
    SFG20_ACCESS_TOKEN = os.environ.get("SFG20_ACCESS_TOKEN")

if "SFG20_SHARE_ID" in os.environ:
    SFG20_SHARE_ID = os.environ.get("SFG20_SHARE_ID")

if "SFG20_URL" in os.environ:
    SFG20_URL = os.environ.get("SFG20_URL")

SFG20_QUERY_001 = """query ExampleQuery {{
  regime(shareLinkId: "{0}", accessToken: "{1}") {{
    words
    guid
    schedules {{
      ... on APISchedule {{
        id
        code
        title
        rawTitle
        rawWhere
        modified
        version
        scheduleCategories
        retired
        skills {{
          ... on APISkill {{
            countTasks
            skill {{
              CoreSkillingID
              Rate
              Skilling
              SkillingCode
              _id
            }}
          }}
        }}
        tasks {{
          ... on APITask {{
            _status
            id
            date
            title
            classification
            intervalInHours
            where
            minutes
            url
            linkId
            content
            fullContent
            fullHtmlContent
            steps
            frequency {{
              interval
              period
            }}
            skill {{
              CoreSkillingID
              Rate
              Skilling
              SkillingCode
              _id
            }}
            schedule {{
              code
              version
            }}
          }}
        }}
        assets {{
          ... on APIAsset {{
            id
            tag
            description
        
         }}
        }}
        frequencies {{
          ... on APIFrequency {{
            label
            countSchedules
            countAssets
            countTasks
            intervalInHours
          }}
        }}
      }}
    }}
  }}
}}"""

SFG20_SHP_LIST = "https://graph.microsoft.com/v1.0/sites/{0}/lists/{1}/items"


# -------------------------------------------------
# API Documentation
# -------------------------------------------------

tags_metadata = [
    {
        "name": "Basic",
        "description": "Endpoint without authentication to check the API status.",
    },
    {
        "name": "SFG20",
        "description": "Endpoints to integrate with SFG20 API and our internal cache.",
    },
    {
        "name": "Config",
        "description": "Endpoints to access the configuration data.",
    },
    {
        "name": "Cache",
        "description": "Endpoints to interact with the internal cache.",
    },
]

ADMIN_USER = None
ADMIN_PWD = None

if "ADMIN_USER" in os.environ:
    ADMIN_USER = os.environ.get("ADMIN_USER")

if "ADMIN_PWD" in os.environ:
    ADMIN_PWD = os.environ.get("ADMIN_PWD")
