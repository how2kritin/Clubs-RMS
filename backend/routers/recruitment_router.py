from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from models.club_recruitment.club_recruitment_config import (create_form, delete_form, get_form_applicant_emails,
                                                             get_form_by_id, get_forms_by_club, update_form, )
from schemas.form.form import FormCreate, FormOut, FormUpdate
from utils.database_utils import get_db

router = APIRouter()


@router.post("/forms", response_model=FormOut, status_code=status.HTTP_201_CREATED)
async def create_new_form(form_data: FormCreate, db: Session = Depends(get_db)):
    try:
        new_form = await create_form(db, form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return new_form


@router.get("/forms/club/{club_id}", response_model=List[FormOut])
async def get_all_forms(club_id: str, db: Session = Depends(get_db)):
    try:
        forms = await get_forms_by_club(db, club_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return forms


@router.get("/forms/{form_id}", response_model=FormOut)
async def get_form(form_id: int, db: Session = Depends(get_db)):
    try:
        form = await get_form_by_id(db, form_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return form


@router.put("/forms/{form_id}", response_model=FormOut)
async def update_existing_form(form_id: int, form_data: FormUpdate, db: Session = Depends(get_db)):
    try:
        updated_form = await update_form(db, form_id, form_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return updated_form


@router.delete("/forms/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_form(form_id: int, db: Session = Depends(get_db)):
    try:
        await delete_form(db, form_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/forms/{form_id}/applicants/emails", response_model=List[str])
async def get_applicants_emails(form_id: int, db: Session = Depends(get_db)):
    try:
        emails = await get_form_applicant_emails(db, form_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return emails
