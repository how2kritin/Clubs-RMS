from typing import List, Optional  # Added for Pydantic model

from pydantic import BaseModel, Field  # Added for request body validation


class UserProfileUpdate(BaseModel):
    hobbies: Optional[str] = None  # Allow null/empty string from frontend
    skills: Optional[List[str]] = None  # Allow empty list
    profile_picture: Optional[int] = Field(
        None, ge=0, le=4
    )  # Validate range 0-4 (assuming 5 pictures)

    class Config:
        from_attributes = True  # Enable ORM mode equivalent for Pydantic v2+


class UserData(BaseModel):
    uid: str
    email: str
    first_name: str
    last_name: str
    roll_number: str
    batch: str
    profile_picture: int

    class Config:
        from_attributes = True  # Enable ORM mode equivalent for Pydantic v2+
