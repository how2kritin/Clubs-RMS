from typing import List, Optional
from pydantic import BaseModel, Field


class UserHabitsData(BaseModel):
    uid: str
    hobbies: Optional[str] = None  # Allow null/empty string from frontend
    skills: Optional[List[str]] = None  # Allow empty list

    class Config:
        from_attributes = True  # Enable ORM mode equivalent for Pydantic v2+
