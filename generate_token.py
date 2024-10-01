# -*- coding: utf-8 -*-
"""
  Generate a token for the dataverse api
  THIS IS NOT BEING USED CURRENTLY, AS THE API 
  DO NOT CONNECT WITH DATAVERSE ANYMORE
"""

from services import dataverse as sv_dataverse
from libs import config

session, token = sv_dataverse.getAuthenticatedSession()

if token:
    open(config.CACHEFILE, "w").write(token.serialize())
