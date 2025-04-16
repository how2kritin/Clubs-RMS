from typing import List

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from models.clubs.clubs_config import (
    fetch_club_by_id,
    fetch_info_about_all_clubs,
    is_subscribed,
    subscribe,
    unsubscribe,
)
from schemas.clubs.clubs import ClubOut
from utils.database_utils import get_db
from utils.session_utils import get_current_user

router = APIRouter()


# Get info about all the clubs.
@router.get("/all_clubs", response_model=List[ClubOut], status_code=status.HTTP_200_OK)
async def get_all_club_information(db: Session = Depends(get_db)):
    return await fetch_info_about_all_clubs(db)


# Get info about a specific club by CID.
@router.get("/{cid}", response_model=ClubOut, status_code=status.HTTP_200_OK)
async def get_club_by_id(cid: str, db: Session = Depends(get_db)):
    return await fetch_club_by_id(cid, db)


@router.get("/is_subscribed/{cid}", response_model=bool, status_code=status.HTTP_200_OK)
def get_subscription_status(
    cid: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    return is_subscribed(cid, current_user["uid"], db)


@router.post("/subscribe/{cid}", response_model=ClubOut, status_code=status.HTTP_200_OK)
async def create_club_subscription(
    cid: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    return await subscribe(cid, current_user["uid"], db)


@router.post(
    "/unsubscribe/{cid}", response_model=ClubOut, status_code=status.HTTP_200_OK
)
async def remove_club_subscription(
    cid: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    return await unsubscribe(cid, current_user["uid"], db)
