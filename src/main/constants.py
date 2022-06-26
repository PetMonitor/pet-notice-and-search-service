from enum import Enum
from os import getenv

DATABASE_SERVER_URL = getenv("DATABASE_SERVER_URL", "http://127.0.0.1:8000")
FACEBOOK_GRAPH_BASE_URL = getenv("FACEBOOK_GRAPH_BASE_URL", "https://graph.facebook.com/v13.0/")
FACEBOOK_BASE_URL = getenv("FACEBOOK_BASE_URL", "https://www.facebook.com/")
POST_DATE_DELETE_DELTA_DAYS = getenv("POST_DATE_DELETE_DELTA", "365")
GROUP_ID = getenv("GROUP_ID", "106287571429551")
FB_PAGE_ACCESS_TOKEN = getenv("FB_PAGE_ACCESS_TOKEN", "")
FB_USER_ACCESS_TOKEN = getenv("FB_USER_ACCESS_TOKEN", "")

class PostState(Enum):
    LOST = "LOST"
    FOUND = "FOUND"

    def __str__(self):
        return str(self.value)