from fastapi import APIRouter, status, Body
from pydantic import BaseModel
from typing import List, Dict, Any
import json

router = APIRouter()


# Define Pydantic models to validate the incoming JSON data
class TimeRange(BaseModel):
    startTime: str
    endTime: str


class DateSchedule(BaseModel):
    date: str
    timeRanges: List[TimeRange]


class InterviewSchedule(BaseModel):
    slotDurationMinutes: int
    interviewPanelCount: int
    dates: List[DateSchedule]
    totalInterviewSlots: int


class FormDataStructure(BaseModel):
    interviewSchedule: InterviewSchedule


@router.post("/schedule_interviews", status_code=status.HTTP_200_OK)
async def schedule_interviews(form_data: FormDataStructure = Body(...)):
    print("Received interview schedule data:")
    print(json.dumps(form_data.model_dump(), indent=2))

    return {"message": "Interviews scheduled successfully"}
