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

if "SFG20_ACCESS_TOKEN" in os.environ:
    SFG20_ACCESS_TOKEN = os.environ.get("SFG20_ACCESS_TOKEN")

if "SFG20_SHARE_ID" in os.environ:
    SFG20_SHARE_ID = os.environ.get("SFG20_SHARE_ID")

if "SFG20_URL" in os.environ:
    SFG20_URL = os.environ.get("SFG20_URL")

# Cache DB configuration
CACHE_DB = "data/cache.db"
CACHE_DB_FIELDS = {
    "schedules": ["id", "code", "title", "rawTitle"],
    "skills": ["skill.CoreSkillingID", "skill.Skilling", "skill.SkillingCode"],
    "tasks": ["id", "title"],
    "assets": ["id", "description"],
    "frequencies": ["label", "label"],
    "classification": ["classification", "classification"],
}
# Dataverse Configuration
DV_SELECTED_TABLE = "cr17a_test_tbls"
DV_SELECTED_FIELDS = ["cr17a_id", "cr17a_name"]

# SFG20 GraphSQL Queries
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
