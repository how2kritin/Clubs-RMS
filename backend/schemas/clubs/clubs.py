from typing import Optional
from pydantic import BaseModel


class ClubResponse(BaseModel):
    cid: str
    name: str
    category: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    banner: Optional[str] = None
    email: Optional[str] = None
    socials: Optional[dict] = None

    class Config:
        orm_mode = True
