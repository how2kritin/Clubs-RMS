from os import getenv

from cas import CASClient
from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from models.habits.habits_config import get_or_create, update_habits
from schemas.habits.habits import UserHabitsData
from utils.database_utils import get_db

CAS_SERVER_URL = getenv("CAS_SERVER_URL")
CAS_SERVICE_URL = f"{getenv('BASE_URL')}/{getenv('SUBPATH', 'api')}/user/login"
cas_client = CASClient(
    version=3, service_url=CAS_SERVICE_URL, server_url=CAS_SERVER_URL
)

router = APIRouter(
    tags=["User Authentication & Profile"],
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)


@router.get(
    "/habits/{uid}",
    status_code=status.HTTP_200_OK,
    summary="Get User Habits",
    description="Retrieves habits of the given uid",
    response_description="skills and hobbies of the given user",
    response_model=UserHabitsData,
)
def get_user_habits(uid: str, db: Session = Depends(get_db)):
    return get_or_create(uid, db)


@router.put(
    "/habits",
    status_code=status.HTTP_200_OK,
    summary="Update User Habits",
    description="Updates habits of the given uid",
    response_description="skills and hobbies of the given user",
    response_model=UserHabitsData,
)
def update_user_habits(habits_data: UserHabitsData, db: Session = Depends(get_db)):
    return update_habits(habits_data, db)
