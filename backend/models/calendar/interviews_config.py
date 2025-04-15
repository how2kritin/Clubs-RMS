from pydantic import BaseModel
from typing import List, Tuple
from datetime import datetime, timedelta


# Pydantic models to validate the incoming JSON data
class TimeRangeStr(BaseModel):
    startTime: str
    endTime: str


class TimeRange(BaseModel):
    startTime: datetime
    endTime: datetime


class DateScheduleStr(BaseModel):
    date: str
    timeRanges: List[TimeRangeStr]


class DateSchedule(BaseModel):
    date: datetime
    timeRanges: List[TimeRange]


class InterviewScheduleStr(BaseModel):
    slotDurationMinutes: int
    interviewPanelCount: int
    dates: List[DateScheduleStr]
    totalInterviewSlots: int


class InterviewSchedule(BaseModel):
    slotDurationMinutes: int
    interviewPanelCount: int
    dates: List[DateSchedule]
    totalInterviewSlots: int


class ScheduleInterviewFormResponseStr(BaseModel):
    interviewSchedule: InterviewScheduleStr


class ScheduleInterviewFormResponse(BaseModel):
    interviewSchedule: InterviewSchedule


def parse_schedule_interview_form_data(
    form_data: ScheduleInterviewFormResponseStr,
) -> ScheduleInterviewFormResponse:
    def intervals_non_overlapping(intervals: List[Tuple[datetime, datetime]]):
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


def calculate_interview_slots(
    form_data: ScheduleInterviewFormResponse,
) -> List[Tuple[datetime | datetime | datetime]]:

    # calculate interview slots based on the form data
    # return a list of tuples (start_time, end_time, date)
    interview_slots: List[Tuple[datetime | datetime | datetime]] = []

    for date_schedule in form_data.interviewSchedule.dates:
        for time_range in date_schedule.timeRanges:
            start_time = datetime.combine(
                date_schedule.date,
                time_range.startTime,
            )
            end_time = datetime.combine(
                date_schedule.date,
                time_range.endTime,
            )
            slot_duration = form_data.interviewSchedule.slotDurationMinutes
            while start_time + timedelta(minutes=slot_duration) <= end_time:
                interview_slots.append(
                    [
                        start_time,
                        start_time + timedelta(minutes=slot_duration),
                        date_schedule.date,
                    ]
                )
                start_time += timedelta(minutes=slot_duration)

    return interview_slots
