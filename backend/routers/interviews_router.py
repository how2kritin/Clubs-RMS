from fastapi import APIRouter, status, Body, HTTPException
import json

from models.calendar.interviews_config import (
    ScheduleInterviewFormResponseStr,
    ScheduleInterviewFormResponse,
    parse_schedule_interview_form_data,
    calculate_interview_slots,
)

router = APIRouter()


@router.post("/schedule_interviews", status_code=status.HTTP_200_OK)
async def schedule_interviews(form_data: ScheduleInterviewFormResponseStr = Body(...)):
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

    # TODO: allocate applicants to slots

    return {"message": "Interviews scheduled successfully"}
