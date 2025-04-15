from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.form.form import FormCreate, FormOut
from utils.database_utils import get_db
from models.club_recruitment.club_recruitment_config import create_form

router = APIRouter()


@router.post("/forms", response_model=FormOut, status_code=status.HTTP_201_CREATED)
def create_new_form(form_data: FormCreate, db: Session = Depends(get_db)):
    try:
        new_form = create_form(db, form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return new_form
