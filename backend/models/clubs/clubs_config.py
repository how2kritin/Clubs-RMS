from sqlalchemy.orm import Session
from models.clubs.clubs_model import Club
from fastapi import status


async def fetch_info_about_all_clubs(db: Session):
    clubs = db.query(Club).all()
    return clubs


async def fetch_club_by_id(cid: str, db: Session):
    club = db.query(Club).filter(Club.cid == cid).first()
    if club is None:
        return status.HTTP_404_NOT_FOUND
    return club
