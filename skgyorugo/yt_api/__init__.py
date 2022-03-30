import urllib3
from dataclasses import dataclass
import os
import json
from typing import Optional

URL = "https://www.googleapis.com/youtube/v3/search"

API = os.getenv("YOUTUBE_API")
CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
