import datetime
from typing import List, Type

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.applications.applications_model import Application
from models.club_recruitment.club_recruitment_model import (
    Form,
    Question,
)
from models.users.users_model import User
from schemas.form.form import FormCreate, FormUpdate


async def create_form(db: Session, form_data: FormCreate) -> Form:
    # raise an exception if deadline is in the past
    if form_data.deadline and (
        form_data.deadline < datetime.datetime.now((datetime.timezone.utc))
    ):
        raise HTTPException(
            status_code=400,
            detail="deadline must be in the future",
        )

    db_form = Form(
        name=form_data.name, club_id=form_data.club_id, deadline=form_data.deadline
    )
    if form_data.questions:
        for question in form_data.questions:
            db_question = Question(
                question_text=question.question_text,
                question_order=question.question_order,
            )
            db_form.questions.append(db_question)

    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form


async def update_form(db: Session, form_id: int, form_data: FormUpdate) -> Type[Form]:
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    if form_data.name is not None:
        form.name = form_data.name  # type: ignore

    if form_data.deadline is not None:
        form.deadline = form_data.deadline  # type: ignore

    # if questions are updated, delete current questions + applications
    if form_data.questions is not None:
        # delete applications + cascaded responses
        db.query(Application).filter(Application.form_id == form_id).delete()

        # delete existing questions
        form.questions.clear()

        # add new questions
        for q in form_data.questions:
            new_q = Question(
                question_text=q.question_text, question_order=q.question_order
            )
            form.questions.append(new_q)

    db.commit()
    db.refresh(form)
    return form


async def delete_form(db: Session, form_id: int) -> None:
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    db.delete(form)
    db.commit()


async def get_form_applicant_emails(db: Session, form_id: int) -> List[str]:
    email_tuples = (
        db.query(User.email)
        .join(Application, Application.user_id == User.uid)
        .filter(Application.form_id == form_id)
        .all()
    )

    emails = [email for (email,) in email_tuples]
    return emails


async def get_form_by_id(db: Session, form_id: int) -> Type[Form] | None:
    form = db.query(Form).filter(Form.id == form_id).first()
    return form


async def get_forms_by_club(db: Session, club_id: str) -> list[Type[Form]]:
    forms = db.query(Form).filter(Form.club_id == club_id).all()
    return forms
