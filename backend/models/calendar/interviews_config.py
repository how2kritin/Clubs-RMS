from pydantic import BaseModel
from typing import List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.calendar.interview_models import (
    InterviewSlot,
    InterviewSchedule,
    InterviewPanel,
)

# from models.calendar.calendar_events_model import CalendarEvent


# Pydantic models to validate the incoming JSON data
class TimeRangeStr(BaseModel):
    startTime: str
    endTime: str


class TimeRangeDatetime(BaseModel):
    startTime: datetime
    endTime: datetime


class DateScheduleStr(BaseModel):
    date: str
    timeRanges: List[TimeRangeStr]


class DateScheduleDatetime(BaseModel):
    date: datetime
    timeRanges: List[TimeRangeDatetime]


class InterviewScheduleStr(BaseModel):
    slotDurationMinutes: int
    interviewPanelCount: int
    dates: List[DateScheduleStr]
    totalInterviewSlots: int


class InterviewScheduleDatetime(BaseModel):
    slotDurationMinutes: int
    interviewPanelCount: int
    dates: List[DateScheduleDatetime]
    totalInterviewSlots: int


class ScheduleInterviewFormResponseStr(BaseModel):
    interviewSchedule: InterviewScheduleStr


class ScheduleInterviewFormResponseDatetime(BaseModel):
    interviewSchedule: InterviewScheduleDatetime


def parse_schedule_interview_form_data(
    form_data: ScheduleInterviewFormResponseStr,
) -> ScheduleInterviewFormResponseDatetime:
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
    form_data: ScheduleInterviewFormResponseDatetime,
) -> List[Tuple[datetime]]:

    # calculate interview slots based on the form data
    # return a list of tuples (start_time, end_time, date)
    interview_slots: List[Tuple[datetime]] = []

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


def create_schedule(
    club_id: str,
    form_id: str,
    slots: List[Tuple[datetime]],
    slot_length: int,
    num_panels: int,
    db: Session,
) -> Tuple[int | List[int]]:

    # create interview schedule
    exisiting_schedule = (
        db.query(InterviewSchedule)
        .filter(
            InterviewSchedule.form_id == form_id,
            InterviewSchedule.club_id == club_id,
        )
        .first()
    )

    if not exisiting_schedule:
        interview_schedule = InterviewSchedule(
            form_id=form_id,
            club_id=club_id,
            slot_length=slot_length,
            num_panels=num_panels,
        )
        db.add(interview_schedule)
        db.commit()
        db.refresh(interview_schedule)
    else:
        interview_schedule = exisiting_schedule

    schedule_id: int = interview_schedule.id

    # create interview slots
    slot_ids: List[int] = []
    for start_time, end_time, date in slots:
        existing_slot = (
            db.query(InterviewSlot)
            .filter(
                InterviewSlot.start_time == start_time,
                InterviewSlot.end_time == end_time,
                InterviewSlot.date == date,
                InterviewSlot.interview_schedule_id == interview_schedule.id,
            )
            .first()
        )

        if not existing_slot:
            interview_slot = InterviewSlot(
                start_time=start_time,
                end_time=end_time,
                date=date,
                interview_schedule_id=interview_schedule.id,
                club_id=club_id,
            )
            db.add(interview_slot)
            db.commit()
            db.refresh(interview_slot)
        else:
            interview_slot = existing_slot

        slot_ids.append(interview_slot.id)

    # create interview panels
    panel_ids: List[int] = []
    for i in range(num_panels):
        existing_panel = (
            db.query(InterviewPanel)
            .filter(
                InterviewPanel.interview_schedule_id == interview_schedule.id,
                InterviewPanel.club_id == club_id,
            )
            .first()
        )

        if not existing_panel:
            interview_panel = InterviewPanel(
                interview_schedule_id=interview_schedule.id,
                club_id=club_id,
            )
            db.add(interview_panel)
            db.commit()
            db.refresh(interview_panel)
        else:
            interview_panel = existing_panel

        panel_ids.append(interview_panel.id)

    return schedule_id, slot_ids, panel_ids
