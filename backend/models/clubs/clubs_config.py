from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from fastapi import HTTPException, status

from models.users.users_model import User
from models.clubs.clubs_model import Club, club_subscribers


async def fetch_info_about_all_clubs(db: Session):
    clubs = db.query(Club).order_by(Club.name).all()
    return clubs


async def fetch_club_by_id(cid: str, db: Session):
    club = db.query(Club).filter(Club.cid == cid).first()
    if club is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Club not found"
        )

    return club


def is_subscribed(cid: str, uid: str, db: Session) -> bool:
    if not db.query(exists().where(Club.cid == cid)).scalar():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Club not found"
        )

    if not db.query(exists().where(User.uid == uid)).scalar():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return db.query(
        exists()
        .where(club_subscribers.c.club_id == cid)
        .where(club_subscribers.c.user_id == uid)
    ).scalar()


async def subscribe(cid: str, uid: str, db: Session):
    club = db.query(Club).filter(Club.cid == cid).first()
    if club is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Club not found"
        )

    user = db.query(User).filter(User.uid == uid).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    club.subscribers.append(user)

    db.commit()
    db.refresh(club)

    return club


async def unsubscribe(cid: str, uid: str, db: Session):
    club = db.query(Club).filter(Club.cid == cid).first()
    if club is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Club not found"
        )

    user = db.query(User).filter(User.uid == uid).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    club.subscribers.remove(user)

    db.commit()
    db.refresh(club)

    return club


def get_all_subscribers(db: Session, cid: str):
    club = db.query(Club).filter(Club.cid == cid).first()
    if club is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Club not found"
        )

    subscribers = club.subscribers
    return subscribers
