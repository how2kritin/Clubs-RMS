from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from schemas.form.form import FormCreate, FormOut, FormUpdate
from utils.database_utils import get_db
from models.club_recruitment.club_recruitment_config import (
    create_form,
    delete_form,
    update_form,
)

router = APIRouter()


@router.post("/forms", response_model=FormOut, status_code=status.HTTP_201_CREATED)
def create_new_form(form_data: FormCreate, db: Session = Depends(get_db)):
    try:
        new_form = create_form(db, form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return new_form


@router.put("/forms/{form_id}", response_model=FormOut)
def update_existing_form(
    form_id: int, form_data: FormUpdate, db: Session = Depends(get_db)
):
    try:
        updated_form = update_form(db, form_id, form_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return updated_form


@router.delete("/forms/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_form(form_id: int, db: Session = Depends(get_db)):
    try:
        delete_form(db, form_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content=form_id, status_code=status.HTTP_204_NO_CONTENT)
