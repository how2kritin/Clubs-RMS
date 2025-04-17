from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from utils.database_utils import Base


class UserHabits(Base):
    __tablename__ = "user_habits"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, nullable=False, index=True)
    hobbies = Column(String, nullable=True)
    skills = Column(JSON, nullable=True)
