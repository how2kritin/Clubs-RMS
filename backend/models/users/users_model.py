from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from utils.database_utils import Base


class UserHabits(Base):
    __tablename__ = "user_habits"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(
        String, ForeignKey("users.uid", ondelete="CASCADE"), nullable=False, index=True
    )
    hobbies = Column(String, nullable=True)
    skills = Column(JSON, nullable=True)

    # optional, for ORM back‐reference
    user = relationship("User", back_populates="habits")


class User(Base):
    __tablename__ = "users"

    uid = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    roll_number = Column(String, unique=True, index=True)
    batch = Column(String, nullable=True)
    profile_picture = Column(Integer, nullable=True)

    habits = relationship(
        "UserHabits",
        back_populates="user",
        uselist=False,  # ← now .habits is a single object
        cascade="all, delete-orphan",
    )
