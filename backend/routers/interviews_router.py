import json
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    status,
    Body,
    HTTPException,
    Cookie,
    Depends,
)
from sqlalchemy.orm import Session

from models.club_recruitment.club_recruitment_model import Form
from models.calendar.interviews_config import (
    ScheduleInterviewFormResponseStr,
    ScheduleInterviewFormResponseDatetime,
    parse_schedule_interview_form_data,
    calculate_interview_slots,
    create_schedule,
    allocate_calendar_events,
)
from routers.users_router import get_current_user
from utils.database_utils import get_db
from utils.session_utils import SESSION_COOKIE_NAME

router = APIRouter(
    tags=["Interviews"],
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden - insufficient permissions"},
        500: {"description": "Internal server error"},
    },
)


@router.post(
    "/schedule_interviews/{form_id}",
    status_code=status.HTTP_200_OK,
    summary="Schedule Interview Slots",
    description="Creates a new interview schedule for a recruitment form with specified time slots and panel configuration.",
    response_description="Confirmation of successful interview scheduling",
    responses={
        400: {
            "description": "Invalid time slots: Overlapping intervals or other validation errors"
        },
        403: {
            "description": "User does not have permission to schedule interviews for this club"
        },
    },
)
async def schedule_interviews(
    form_id: int,
    encrypted_session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: Session = Depends(get_db),
    form_data: ScheduleInterviewFormResponseStr = Body(
        ...,
        description="Interview schedule configuration including dates, time slots, panel count, and slot duration",
        example={
            "formId": 123,
            "interviewSchedule": {
                "dates": ["2025-04-20", "2025-04-21"],
                "timeSlots": [
                    {"startTime": "10:00", "endTime": "12:00"},
                    {"startTime": "14:00", "endTime": "16:00"},
                ],
                "interviewPanelCount": 3,
                "slotDurationMinutes": 30,
            },
        },
    ),
):
    """
    Create a new interview schedule for a recruitment form.

    This endpoint:
    1. Parses and validates the interview schedule data
    2. Calculates all possible interview slots based on the provided configuration
    3. Creates database records for the schedule, slots, and panels
    4. Allocates applicants to interview slots and generates calendar events

    The schedule configuration includes:
    - Dates when interviews will be conducted
    - Time slots on each date (can have multiple slots per day with breaks in between)
    - Number of parallel interview panels
    - Duration of each interview slot in minutes

    - Authentication required: User must be logged in
    - Authorization required: User must be an admin of the club associated with the form
    - Returns confirmation of successful scheduling and creation of calendar events
    """
    print("Received interview schedule data:")
    print(json.dumps(form_data.model_dump(), indent=2))
    print("Form ID:", form_id)

    # check if deadline has passed or not
    recruitment_form = db.query(Form).filter(Form.id == form_id).first()
    if not recruitment_form:
        raise HTTPException(
            status_code=404,
            detail="Form not found",
        )

    # RBAC
    # must be the club account
    cur_user = await get_current_user(encrypted_session_id, db)
    if cur_user["uid"] != recruitment_form.club_id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to schedule interviews for this club.",
        )

    # deadline check
    deadline = recruitment_form.deadline
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) < deadline:
        raise HTTPException(
            status_code=400,
            detail="Form is still active. Cannot schedule interviews.",
        )

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

    # Calculate interview slots based on the provided configuration
    interview_slots = calculate_interview_slots(form_data_parsed)

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

    # # TODO: remove after testing
    # # create applications
    # from models.applications.applications_model import Application
    # from models.users.users_model import User

    # for uid in [
    #     "varun.edachali",
    #     "samyak.mishra",
    #     "shaunak.biswas",
    #     "ashutosh.rudrabhatla",
    #     "kritin.madireddy",
    #     # "vamsi.krishna",
    # ]:
    #     exisiting_user = db.query(User).filter(User.uid == uid).first()
    #     if exisiting_user:
    #         print("User already exists")
    #         user = exisiting_user
    #     else:
    #         user = User(
    #             uid=uid,
    #             email=uid + "@students.iiit.ac.in",
    #             first_name=uid,
    #             last_name=uid,
    #             roll_number=uid,
    #         )
    #         db.add(user)
    #         db.commit()
    #         db.refresh(user)
    #         print("User created successfully")

    #     print(user.uid)
    #     application = Application(
    #         form_id=form_id,
    #         user_id=uid,
    #         status="ongoing",
    #     )

    #     db.add(application)
    #     db.commit()
    #     db.refresh(application)
    #     print("Application created successfully")
    #     print(application.id)

    # allocate applicants to slots
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

    return {
        "success": True,
        "message": "Interviews scheduled successfully",
        "details": {
            "schedule_id": schedule_id,
            "slot_count": len(slot_ids),
            "panel_count": len(panel_ids),
            "event_count": len(event_ids),
        },
    }
