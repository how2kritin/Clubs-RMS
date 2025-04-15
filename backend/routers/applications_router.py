from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.applications.applications_config import update_application_status
from schemas.applications.applications import ApplicationOut, ApplicationStatusUpdate
from utils.database_utils import get_db  # your dependency for DB sessions

router = APIRouter()


@router.put("/applications/{application_id}/status", response_model=ApplicationOut)
def update_application_status_endpoint(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        updated_application = update_application_status(
            db, application_id, status_update
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return updated_application
