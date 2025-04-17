import os
from typing import List
import requests


from schemas.clubs.clubs import ClubOut

# HABITS SERVICE HELPERS

BLOB_SERVICE_URL = os.getenv("BLOB_URL", "http://localhost:8000")


def get_clubs() -> List[ClubOut]:
    """
    Fetches the UserHabitsData for the given UID from the habits microservice.
    Raises HTTPError on non-2xx responses.
    """
    url = f"{BLOB_SERVICE_URL}/api/club/five_clubs"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    return resp.json()
