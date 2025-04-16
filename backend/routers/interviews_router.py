from fastapi import APIRouter, status, Body, HTTPException, Cookie, Depends
import json

from sqlalchemy.orm import Session

from routers.users_router import get_current_user
from utils.database_utils import get_db
from utils.session_utils import SESSION_COOKIE_NAME


from models.calendar.interviews_config import (
    ScheduleInterviewFormResponseStr,
    ScheduleInterviewFormResponseDatetime,
    parse_schedule_interview_form_data,
    calculate_interview_slots,
    create_schedule,
    allocate_calendar_events,
)

router = APIRouter()


@router.post("/schedule_interviews", status_code=status.HTTP_200_OK)
async def schedule_interviews(
    encrypted_session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: Session = Depends(get_db),
    form_data: ScheduleInterviewFormResponseStr = Body(...),
):
    print("Received interview schedule data:")
    print(json.dumps(form_data.model_dump(), indent=2))

    try:
        # convert to date and time and all
        form_data_parsed: ScheduleInterviewFormResponseDatetime = (
            parse_schedule_interview_form_data(form_data)
        )
        print("Parsed interview schedule data:")
        print(form_data_parsed)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid time slots: overlapping intervals detected. Please enter correct time slots.",
        )

    # calculate interview slots and create slots, panels and a schedule
    interview_slots = calculate_interview_slots(form_data_parsed)

    # TODO: RBAC?
    # must be the club account
    cur_user = await get_current_user(encrypted_session_id, db)

    # TODO: remove when testing is done
    # create club with uid
    from models.clubs.clubs_model import Club

    exisiting_club = db.query(Club).filter(Club.cid == cur_user["uid"]).first()
    if exisiting_club:
        print("Club already exists")
        club = exisiting_club
    else:
        print("Creating club")
        club = Club(cid=cur_user["uid"], name="Interview Club")
        db.add(club)
        db.commit()
        db.refresh(club)
        print("Club created successfully")

    # TODO: remove when testing is done
    # TODO: get the form ID from the form data
    from models.club_recruitment.club_recruitment_model import Form

    form = Form(club_id=cur_user["uid"], name="Interview Form")
    db.add(form)
    db.commit()
    db.refresh(form)
    form_id = form.id
    print("Form ID:", form_id)

    schedule_id, slot_ids, panel_ids = create_schedule(
        club_id=cur_user["uid"],
        form_id=form_id,
        slots=interview_slots,
        slot_length=form_data_parsed.interviewSchedule.slotDurationMinutes,
        num_panels=form_data_parsed.interviewSchedule.interviewPanelCount,
        db=db,
    )
    print("Interview schedule created successfully")
    print(schedule_id, slot_ids, panel_ids)

    # TODO: remove after testing
    # create applications
    from models.applications.applications_model import Application
    from models.users.users_model import User

    for uid in [
        "varun.edachali",
        "samyak.mishra",
        "shaunak.biswas",
        "ashutosh.rudrabhatla",
        "kritin.madireddy",
        # "vamsi.krishna",
    ]:
        exisiting_user = db.query(User).filter(User.uid == uid).first()
        if exisiting_user:
            print("User already exists")
        else:
            user = User(
                uid=uid,
                email=uid + "@students.iiit.ac.in",
                first_name=uid,
                last_name=uid,
                roll_number=uid,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("User created successfully")

        print(user.uid)
        application = Application(
            form_id=form_id,
            user_id=uid,
            status="ongoing",
        )

        db.add(application)
        db.commit()
        db.refresh(application)
        print("Application created successfully")
        print(application.id)

    # TODO: allocate applicants to slots
    event_ids = allocate_calendar_events(
        schedule_id=schedule_id,
        slot_ids=slot_ids,
        panel_ids=panel_ids,
        db=db,
        club_id=cur_user["uid"],
        form_id=form_id,
    )
    print("Allocated calendar events successfully")
    print(event_ids)

    return {"message": "Interviews scheduled successfully"}
