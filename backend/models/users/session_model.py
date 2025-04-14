from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from utils.database_utils import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)  # session ID
    user_uid = Column(String, ForeignKey("users.uid"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
