# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

load_dotenv()

GLOBAL_API_KEY = None
WEB_API_URL = None
SCOPE = None
CLIENT_ID = None
AUTHORITY = None
CACHEFILE = None

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


DV_SELECTED_TABLE = "cr17a_test_tbls"
DV_SELECTED_FIELDS = ["cr17a_id", "cr17a_name"]

SFG20_ACCESS_TOKEN = "_hDabVqMQ3dmL0"
SFG20_SHARE_ID = "volI8IHPvDSIKo"
SFG20_URL = "https://api.demo.facilities-iq.com/v3.0"

SFG20_QUERY_001 = """query ListQuery {{ regime(shareLinkId: "{0}", accessToken: "{1}") {{
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
      }}
    }}
    frequencies {{
      ... on APIFrequency {{
        frequency {{
          interval
          period
        }}
        label
        countSchedules
        countAssets
        countTasks
        intervalInHours
      }}
    }}
    skills {{
      ... on APISkill {{
        skill {{
          CoreSkillingID
          Rate
          Skilling
          SkillingCode
          _id
        }}
        countTasks
      }}
    }}
    assets {{
      ... on APIAsset {{
        id
        tag
        description
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
    groups {{
      ... on APIGroup {{
        id
        title
        details
        type
        taskCount
        scheduleCount
        assetCount
        frequencyCount
        parentGroupId
      }}
    }}
  }}
}}"""
