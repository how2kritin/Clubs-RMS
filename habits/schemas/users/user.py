from pydantic import BaseModel


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
