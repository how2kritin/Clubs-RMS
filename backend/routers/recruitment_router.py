from typing import List

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from models.club_recruitment.club_recruitment_config import (
    create_form,
    delete_form,
    get_form_applicant_emails,
    get_form_by_id,
    get_forms_by_club,
    inform_users,
    update_form,
)
from models.clubs.clubs_config import get_all_subscribers
from models.users.users_config import is_admin_of_club, is_member_of_club
from schemas.form.form import FormCreate, FormOut, FormUpdate
from utils.database_utils import get_db
from utils.session_utils import SESSION_COOKIE_NAME, get_current_user

router = APIRouter()


@router.post("/forms", status_code=status.HTTP_201_CREATED, response_model=FormOut)
async def create_new_form(
    form_data: FormCreate,
    encrypted_session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: Session = Depends(get_db),
):
    try:
        user = await get_current_user(encrypted_session_id, db)
        if not is_admin_of_club(user["uid"], form_data.club_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to create a form for this club.",
            )
        new_form = await create_form(db, form_data)

        subject = f"New Hiring Round Created: {new_form.name}"
        content = (
            f"A new hiring round has been created by the club {new_form.club_id}.\n"
            + "head to clubs-plus-plus to see more!\n"
        )

        subscribers = get_all_subscribers(db, new_form.club_id)  # type: ignore
        inform_users(subscribers, subject, content)
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
async def update_existing_form(
    form_id: int,
    form_data: FormUpdate,
    encrypted_session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: Session = Depends(get_db),
):
    try:
        user = await get_current_user(encrypted_session_id, db)
        form = await get_form_by_id(db, form_id)
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        if not (
            is_member_of_club(user["uid"], form.club_id, db)  # type: ignore
            or is_admin_of_club(user["uid"], form.club_id, db)  # type: ignore
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to create a form for this club.",
            )

        updated_form = await update_form(db, form_id, form_data)

        subject = f"Hiring Round Updated: {updated_form.name}"
        content = (
            f"hiring round {updated_form.name} has been updated by the club {updated_form.club_id}.\n"
            + "head to clubs-plus-plus to see more!\n"
        )

        subscribers = get_all_subscribers(db, updated_form.club_id)  # type: ignore
        inform_users(subscribers, subject, content)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return updated_form


@router.delete("/forms/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_form(
    form_id: int,
    encrypted_session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: Session = Depends(get_db),
):
    try:
        user = await get_current_user(encrypted_session_id, db)
        form = await get_form_by_id(db, form_id)
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        if not is_admin_of_club(user["uid"], form.club_id, db):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to create a form for this club.",
            )
        subscribers = get_all_subscribers(db, form.club_id)  # type: ignore

        await delete_form(db, form_id)

        subject = f"Hiring Round to be Deleted: {form.name}"
        content = (
            f"hiring round {form.name} will be deleted by the club {form.club_id}.\n"
        )

        inform_users(subscribers, subject, content)
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
