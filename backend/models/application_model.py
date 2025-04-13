import enum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from utils.database_utils import Base


class ApplicationStatus(enum.Enum):
    ongoing = "ongoing"
    under_review = "under review"
    accepted = "accepted"
    rejected = "rejected"


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="applications")

    # TODO: what exactly is the club identifier?
    club_id = Column(String, nullable=False)

    form_response = Column(JSON)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.ongoing)
