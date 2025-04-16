from fastapi import APIRouter, status, Body, HTTPException, Cookie, Depends


from sqlalchemy import or_
from sqlalchemy.orm import Session

from routers.users_router import get_current_user
from utils.database_utils import get_db
from utils.session_utils import SESSION_COOKIE_NAME


from models.clubs.clubs_model import Club, club_members
from models.calendar.calendar_events_model import CalendarEvent


router = APIRouter()


@router.get("/events", status_code=status.HTTP_200_OK)
async def schedule_interviews(
    encrypted_session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: Session = Depends(get_db),
):

    # TODO: RBAC?
    # must be the club account
    cur_user = await get_current_user(encrypted_session_id, db)

    # get clubs the user is a member of
    club_ids = list(
        club.cid
        for club in db.query(Club)
        .join(club_members)
        .filter(club_members.c.user_id == cur_user["uid"])
        .all()
    )

    print("Clubs fetched successfully")
    print(club_ids)

    # get events the user can see
    # if the visible field is their uid
    # or if the club field is of a club they are a member of
    # or if the user is the club account
    events = list(
        event.to_dict()
        for event in db.query(CalendarEvent)
        .filter(
            or_(
                CalendarEvent.visible_to_user == cur_user["uid"],
                CalendarEvent.club_id.in_(club_ids),
                CalendarEvent.club_id == cur_user["uid"],
            )
        )
        .all()
    )

    print("Events fetched successfully")
    print(events)
    return events
