import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    Text,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from utils.database_utils import Base

from datetime import datetime, timezone


class ApplicationStatus(enum.Enum):
    ongoing = "ongoing"
    under_review = "under review"
    accepted = "accepted"
    rejected = "rejected"


class Form(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False, unique=True)
    club_id = Column(Integer, nullable=True)
    __table_args__ = (UniqueConstraint("club_id", "name", name="uq_club_id_form_name"),)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    questions = relationship(
        "Question", back_populates="form", cascade="all, delete-orphan"
    )
    applications = relationship(
        "Application", back_populates="form", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    form_id = Column(
        Integer, ForeignKey("forms.id", ondelete="CASCADE"), nullable=False
    )
    question_text = Column(Text, nullable=False)
    question_order = Column(Integer, nullable=True)

    form = relationship("Form", back_populates="questions")
    responses = relationship(
        "Response", back_populates="question", cascade="all, delete-orphan"
    )


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    form_id = Column(
        Integer, ForeignKey("forms.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    submitted_at = Column(DateTime, default=datetime.now(timezone.utc))

    form = relationship("Form", back_populates="applications")
    responses = relationship(
        "Response", back_populates="application", cascade="all, delete-orphan"
    )

    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.ongoing)


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)

    application_id = Column(
        Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False
    )
    question_id = Column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    answer_text = Column(Text, nullable=True)

    application = relationship("Application", back_populates="responses")
    question = relationship("Question", back_populates="responses")
