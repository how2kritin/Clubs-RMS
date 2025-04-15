from typing import List

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from models.clubs.clubs_model import Club
from schemas.clubs.clubs import ClubResponse
from utils.database_utils import get_db

router = APIRouter()


# Get info about all the clubs.
@router.get(
    "/all_clubs", response_model=List[ClubResponse], status_code=status.HTTP_200_OK
)
async def get_all_club_information(db: Session = Depends(get_db)):
    clubs = db.query(Club).order_by(Club.name).all()
    return clubs


# Get info about a specific club by CID.
@router.get("/{cid}", response_model=ClubResponse, status_code=status.HTTP_200_OK)
async def get_club_by_id(cid: str, db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.cid == cid).first()
    if club is None:
        return status.HTTP_404_NOT_FOUND
    return club
