from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON  # Use this if your DB supports PostgreSQL JSON type
from utils.database_utils import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    # Replacing first_name and last_name with a single name field to match the TSX file
    name = Column(String, nullable=False)
    roll_number = Column(String, unique=True, index=True)
    # New fields from the user profile page:
    hobbies = Column(String, nullable=True)
    skills = Column(JSON, nullable=True)  # Alternatively, use a comma-separated String if JSON is not an option.
    gender = Column(String, nullable=True)  # Expected values: 'Male', 'Female', 'Other', 'Prefer not to say'
    batch = Column(String, nullable=True)   # Expected values: 'UG1', 'UG2', 'UG3', 'UG4', 'UG5', 'PG1', 'PG2', 'PHD'
    profile_picture = Column(Integer, nullable=True)  # Store image number
    is_active = Column(Boolean, default=True)
