import os
import requests


from schemas.user.habits import UserHabitsData

# HABITS SERVICE HELPERS

HABITS_SERVICE_URL = os.getenv("HABITS_URL", "http://localhost:8000")


def get_habits(user_id: str) -> UserHabitsData:
    """
    Fetches the UserHabitsData for the given UID from the habits microservice.
    Raises HTTPError on non-2xx responses.
    """
    url = f"{HABITS_SERVICE_URL}/habit/{user_id}"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    # resp.json() should match UserHabitsData schema
    return UserHabitsData(**resp.json())


def update_habits(habits_data: UserHabitsData) -> None:
    """
    Sends the updated habits_data to the microservice via PUT.
    Raises HTTPError on non-2xx responses.
    """
    url = f"{HABITS_SERVICE_URL}/habit"
    # Pydantic v2: use .model_dump(); v1: .dict()
    payload = (
        habits_data.model_dump()
        if hasattr(habits_data, "model_dump")
        else habits_data.dict()
    )
    resp = requests.put(url, json=payload, timeout=5)
    resp.raise_for_status()
