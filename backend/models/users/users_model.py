from sqlalchemy import Column, String
from utils.database_utils import Base

class User(Base):
    __tablename__ = "users"

    uid = Column(String, unique=True, index=True, primary_key=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    roll_number = Column(String, unique=True, index=True)