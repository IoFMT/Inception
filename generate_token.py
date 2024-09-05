from services import dataverse as sv_dataverse
from libs import config

session, token = sv_dataverse.getAuthenticatedSession()

if token:
    open(config.CACHEFILE, "w").write(token.serialize())
