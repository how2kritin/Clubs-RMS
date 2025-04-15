from fastapi import APIRouter, status, Body, HTTPException
from pydantic import BaseModel
from typing import List, Tuple, Dict, Any
from datetime import datetime
import json

router = APIRouter()


# Pydantic models to validate the incoming JSON data
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


class ScheduleInterviewFormResponse(BaseModel):
    interviewSchedule: InterviewSchedule


def parse_schedule_interview_form_data(form_data: ScheduleInterviewFormResponse):
    def intervals_non_overlapping(intervals: List[Tuple]):
        intervals.sort(key=lambda x: x[0])
        for (s1, e1), (s2, _) in zip(intervals, intervals[1:]):
            if s2 < e1:
                return False
        return True

    # convert all dates and times to datetime objects
    for date_schedule in form_data.interviewSchedule.dates:
        date_schedule.date = datetime.strptime(
            date_schedule.date,
            "%Y-%m-%d",
        ).date()
        for time_range in date_schedule.timeRanges:
            time_range.startTime = datetime.strptime(
                time_range.startTime, "%H:%M"
            ).time()
            time_range.endTime = datetime.strptime(
                time_range.endTime,
                "%H:%M",
            ).time()

        # validate time intervals
        if not intervals_non_overlapping(
            [
                (time_range.startTime, time_range.endTime)
                for time_range in date_schedule.timeRanges
            ]
        ):
            raise ValueError("Overlapping time intervals detected")

    return form_data


@router.post("/schedule_interviews", status_code=status.HTTP_200_OK)
async def schedule_interviews(form_data: ScheduleInterviewFormResponse = Body(...)):
    print("Received interview schedule data:")
    print(json.dumps(form_data.model_dump(), indent=2))

    try:
        # convert to date and time and all
        form_data = parse_schedule_interview_form_data(form_data)
        print("Parsed interview schedule data:")
        print(form_data)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid time slots: overlapping intervals detected. Please enter correct time slots.",
        )

    return {"message": "Interviews scheduled successfully"}
