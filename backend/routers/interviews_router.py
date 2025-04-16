import json

from fastapi import APIRouter, status, Body, HTTPException, Cookie, Depends
from sqlalchemy.orm import Session

from models.calendar.interviews_config import (ScheduleInterviewFormResponseStr, ScheduleInterviewFormResponseDatetime,
                                               parse_schedule_interview_form_data, calculate_interview_slots,
                                               create_schedule, )
from routers.users_router import get_current_user
from utils.database_utils import get_db
from utils.session_utils import SESSION_COOKIE_NAME

router = APIRouter()


@router.post("/schedule_interviews", status_code=status.HTTP_200_OK)
async def schedule_interviews(encrypted_session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME),
        db: Session = Depends(get_db), form_data: ScheduleInterviewFormResponseStr = Body(...), ):
    print("Received interview schedule data:")
    print(json.dumps(form_data.model_dump(), indent=2))

    try:
        # convert to date and time and all
        form_data_parsed: ScheduleInterviewFormResponseDatetime = (parse_schedule_interview_form_data(form_data))
        print("Parsed interview schedule data:")
        print(form_data_parsed)
    except ValueError as e:
        raise HTTPException(status_code=400,
            detail="Invalid time slots: overlapping intervals detected. Please enter correct time slots.", )

    # calculate interview slots and create slots, panels and a schedule
    interview_slots = calculate_interview_slots(form_data_parsed)

    # TODO: RBAC?
    # must be the club account
    cur_user = await get_current_user(encrypted_session_id, db)

    # TODO: get the form ID from the form data
    form_id = 1
    from models.applications.applications_model import Form
    form = Form(id=form_id, club_id=cur_user["uid"])
    db.add(form)
    db.commit()
    db.refresh(form)

    schedule_id, slot_ids, panel_ids = create_schedule(club_id=cur_user["uid"], form_id=form_id, slots=interview_slots,
        slot_length=form_data_parsed.interviewSchedule.slotDurationMinutes,
        num_panels=form_data_parsed.interviewSchedule.interviewPanelCount, db=db, )
    print("Interview schedule created successfully")
    print(schedule_id, slot_ids, panel_ids)

    # TODO: allocate applicants to slots

    return {"message": "Interviews scheduled successfully"}
