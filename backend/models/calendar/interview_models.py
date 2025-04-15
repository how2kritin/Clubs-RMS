from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    Time,
    Date,
)
from sqlalchemy.orm import relationship
from utils.database_utils import Base


class InterviewSlot(Base):
    __tablename__ = "interview_slot"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    date = Column(Date, nullable=False)

    interview_schedule_id = Column(
        Integer,
        ForeignKey("interview_schedule.id"),
        nullable=False,
    )
    interview_schedule = relationship(
        "InterviewSchedule",
        backref="interview_slot",
    )

    club_id = Column(
        String,
        ForeignKey("clubs.cid"),
        nullable=False,
    )
    # club = relationship(
    #     "Club",
    #     backref="interview_slot",
    # )


class InterviewPanel(Base):
    __tablename__ = "interview_panel"

    id = Column(Integer, primary_key=True, index=True)

    interview_schedule_id = Column(
        Integer,
        ForeignKey("interview_schedule.id"),
        nullable=False,
    )
    interview_schedule = relationship(
        "InterviewSchedule",
        backref="interview_panel",
    )

    club_id = Column(
        String,
        ForeignKey("clubs.cid"),
        nullable=False,
    )
    # club = relationship(
    #     "Club",
    #     backref="interview_panel",
    # )

    # num_interviewers = Column(Integer, nullable=False)
    # TODO: add interview names?


class InterviewSchedule(Base):
    __tablename__ = "interview_schedule"

    id = Column(Integer, primary_key=True, index=True)

    form_id = Column(
        Integer,
        ForeignKey("forms.id"),
        nullable=False,
    )
    # form = relationship(
    #     "Form",
    #     backref="interview_schedule",
    # )

    # TODO: check with CC data/dummy data
    club_id = Column(
        String,
        ForeignKey("clubs.cid"),
        nullable=False,
    )
    # club = relationship(
    #     "Club",
    #     backref="interview_schedule",
    # )

    slot_length = Column(Integer, nullable=False)  # in minutes
    num_panels = Column(Integer, nullable=False)
