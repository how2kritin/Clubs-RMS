from sqlalchemy.orm import Session
from models.club_recruitment.club_recruitment_model import (
    Form,
    Question,
)
from schemas.form.form import FormCreate


def create_form(db: Session, form_data: FormCreate) -> Form:
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
