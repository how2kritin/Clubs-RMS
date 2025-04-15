from typing import List

from fastapi import APIRouter, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.clubs.clubs_model import Club
from utils.database_utils import get_db

router = APIRouter()


class ClubResponse(BaseModel):
    id: int
    cid: str
    name: str
    category: str = None
    tagline: str = None
    description: str = None
    logo: str = None
    banner: str = None
    email: str = None
    socials: dict = None

    class Config:
        orm_mode = True


# Get info about all the clubs.
@router.get("/clubs/", response_model=List[ClubResponse], status_code=status.HTTP_200_OK)
async def get_all_club_information(db: Session = Depends(get_db)):
    clubs = db.query(Club).all()
    return clubs


# Get info about a specific club by CID.
@router.get("/clubs/{cid}", response_model=ClubResponse, status_code=status.HTTP_200_OK)
async def get_club_by_id(cid: str, db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.cid == cid).first()
    if club is None:
        return status.HTTP_404_NOT_FOUND
    return club
