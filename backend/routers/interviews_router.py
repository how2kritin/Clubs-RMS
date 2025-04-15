from fastapi import APIRouter, status, Body, HTTPException, Cookie
import json

from sqlalchemy.orm import Session

from routers.users_router import get_user_info, get_current_user
from utils.database_utils import get_db
from utils.session_utils import SESSION_COOKIE_NAME, validate_session
from fastapi import Depends


from models.calendar.interviews_config import (
    ScheduleInterviewFormResponseStr,
    ScheduleInterviewFormResponse,
    parse_schedule_interview_form_data,
    calculate_interview_slots,
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
        form_data_parsed: ScheduleInterviewFormResponse = (
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

    cur_user = await get_current_user(encrypted_session_id, db)
    print(cur_user)

    # TODO: allocate applicants to slots

    return {"message": "Interviews scheduled successfully"}
