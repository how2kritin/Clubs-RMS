from sqlalchemy.orm import Session
from models.applications.applications_model import Application
from schemas.applications.applications import ApplicationStatusUpdate

from fastapi import HTTPException


def update_application_status(
    db: Session, application_id: int, status_update: ApplicationStatusUpdate
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = status_update.status  # type: ignore

    db.commit()
    db.refresh(application)
    return application
