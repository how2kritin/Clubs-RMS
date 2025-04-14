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

    id = Column(Integer, primary_key=True, index=True)  # primary key of the DB
    club_id = Column(String, nullable=False)  # like UID for users, except for clubs

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="applications")

    form_response = Column(JSON)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.ongoing)