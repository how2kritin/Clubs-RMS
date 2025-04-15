from pydantic import BaseModel
from datetime import datetime

from models.applications.applications_model import ApplicationStatus


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationOut(BaseModel):
    id: int
    form_id: int
    user_id: int
    submitted_at: datetime
    status: ApplicationStatus

    class Config:
        orm_mode = True
