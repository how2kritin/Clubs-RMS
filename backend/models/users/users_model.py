from sqlalchemy import Boolean, Column, Integer, String, event
from sqlalchemy.dialects.postgresql import JSON
from utils.database_utils import Base

class User(Base):
    __tablename__ = "users"

    uid = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    roll_number = Column(String, unique=True, index=True)
    hobbies = Column(String, nullable=True)
    skills = Column(JSON, nullable=True) 
    batch = Column(String, nullable=True)
    profile_picture = Column(Integer, nullable=True)  

IMMUTABLE_FIELDS = {"uid", "roll_number", "email", "first_name", "last_name"}

@event.listens_for(User, "load")
def receive_load(user, _):
    user._original_values = {field: getattr(user, field) for field in IMMUTABLE_FIELDS}

@event.listens_for(User, "before_update")
def before_update(mapper, connection, target):
    for field in IMMUTABLE_FIELDS:
        original = target._original_values.get(field)
        current = getattr(target, field)
        if original != current:
            raise ValueError(f"Field '{field}' is immutable and cannot be changed.")
