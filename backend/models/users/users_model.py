from sqlalchemy import Column, String
from utils.database_utils import Base

class User(Base):
    __tablename__ = "users"

    uid = Column(String, unique=True, primary_key=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    roll_number = Column(String, unique=True, nullable=False)