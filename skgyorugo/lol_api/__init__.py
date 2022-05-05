import urllib3
from dataclasses import dataclass
import os
import json
import logging
from typing import Optional

BASE_URL = "https://euw1.api.riotgames.com"

KEY = os.getenv("LOL_STREAM_HELPER")

HEADER = {"X-Riot-Token": KEY}
