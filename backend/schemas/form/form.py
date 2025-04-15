from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class QuestionCreate(BaseModel):
    question_text: str
    question_order: Optional[int] = None


class FormCreate(BaseModel):
    name: str
    club_id: Optional[str] = None
    deadline: Optional[datetime] = None
    questions: Optional[List[QuestionCreate]] = []


class FormUpdate(BaseModel):
    name: Optional[str] = None
    deadline: Optional[datetime] = None
    questions: Optional[List[QuestionCreate]] = None


class QuestionOut(BaseModel):
    id: int
    question_text: str
    question_order: Optional[int]

    class Config:
        orm_mode = True


class FormOut(BaseModel):
    id: int
    name: str
    club_id: Optional[str] = None
    deadline: Optional[datetime] = None
    created_at: datetime
    questions: List[QuestionOut] = []

    class Config:
        orm_mode = True
