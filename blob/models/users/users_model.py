from sqlalchemy import Column, Integer, String

from utils.database_utils import Base


class User(Base):
    __tablename__ = "users"

    uid = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    roll_number = Column(String, unique=True, index=True)
    batch = Column(String, nullable=True)
    profile_picture = Column(Integer, nullable=True)
