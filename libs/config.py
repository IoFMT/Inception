# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

load_dotenv()

GLOBAL_API_KEY = None
if "GLOBAL_API_KEY" in os.environ:
    GLOBAL_API_KEY = os.environ["GLOBAL_API_KEY"]
