import enum
from sqlalchemy import (
    Column,
    Integer,
    Enum,
    ForeignKey,
    Text,
    DateTime,
    UniqueConstraint,

    String,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from utils.database_utils import Base

from datetime import datetime, timezone


class ApplicationStatus(enum.Enum):
    ongoing = "ongoing"
    under_review = "under review"
    accepted = "accepted"
    rejected = "rejected"


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    form_id = Column(
        Integer, ForeignKey("forms.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        String, ForeignKey("users.uid", ondelete="CASCADE"), nullable=False
    )
    __table_args__ = (
        UniqueConstraint("user_id", "form_id", name="uq_user_id_form_id"),

    )

    submitted_at = Column(DateTime, default=datetime.now(timezone.utc))

    form = relationship("Form", back_populates="applications")
    responses = relationship(
        "Response", back_populates="application", cascade="all, delete-orphan"
    )

    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.ongoing)

    # TODO: referential integrity through user ids?
    endorser_ids = Column(ARRAY(String), default=[])


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
