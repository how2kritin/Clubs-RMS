from sqlalchemy.orm import Session
from models.applications.applications_model import Application
from utils.database_utils import get_db


def get_applicants_by_form(form_id: int):
    db: Session = next(get_db())
    try:
        applicants = db.query(Application).filter(Application.form_id == form_id).all()
        return applicants
    finally:
        db.close()


if __name__ == "__main__":
    form_id = 1  # form ID
    applications = get_applicants_by_form(form_id)
    for application in applications:
        print(
            f"User ID: {application.user_id}, Submitted At: {application.submitted_at}"
        )
