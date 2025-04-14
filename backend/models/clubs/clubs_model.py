from sqlalchemy import Boolean, Column, Integer, String
from utils.database_utils import Base

class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
