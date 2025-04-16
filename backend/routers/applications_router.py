from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.applications.applications_config import get_application_autofill_info, process_submitted_application, \
    get_application_status, update_application_status, endorse_application, delete_application
from schemas.applications.applications import ApplicationOut, ApplicationStatusUpdate
from utils.database_utils import get_db

router = APIRouter()


# Get the information needed to autofill some fields of an application.
@router.get("/")
async def get_application_autofill_info_endpoint():
    return await get_application_autofill_info()


# Process a submitted application.
@router.post("/")
async def process_submitted_application_endpoint():
    return await process_submitted_application()


# Get the current status of a submitted application.
@router.get("/{application_id}/status")
async def get_application_status_endpoint(application_id: int):
    return await get_application_status()


# Update status of an application.
@router.put("/{application_id}/status", response_model=ApplicationOut)
async def update_application_status_endpoint(application_id: int, status_update: ApplicationStatusUpdate,
                                             db: Session = Depends(get_db), ):
    try:
        updated_application = await update_application_status(db, application_id, status_update)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return updated_application


# Endorse an application.
@router.put("/{application_id}/endorse")
async def endorse_application_endpoint(application_id: int):
    return await endorse_application()


# Delete an application.
@router.delete("/{application_id}")
async def delete_application_endpoint(application_id: int):
    return await delete_application()
