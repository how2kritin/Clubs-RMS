from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from utils.database_utils import Base

from datetime import datetime, timezone


class Form(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False, unique=True)
    club_id = Column(Integer, nullable=True)
    __table_args__ = (UniqueConstraint("club_id", "name", name="uq_club_id_form_name"),)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    deadline = Column(DateTime, nullable=True, default=datetime.now(timezone.utc))

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
