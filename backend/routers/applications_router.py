from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from models.applications.applications_config import (
    get_application_autofill_info,
    process_submitted_application,
    get_application_status,
    update_application_status,
    endorse_application,
    withdraw_endorsement,
    delete_application,
    get_application_details,
    get_user_applications,
    get_form_applications,
)
from schemas.applications.applications import (
    ApplicationOut,
    ApplicationStatusUpdate,
    UserApplicationOut,
    FormApplicationOut,
)
from utils.database_utils import get_db
from utils.session_utils import get_current_user

router = APIRouter()


# Get the information needed to autofill some fields of an application.
@router.get("/autofill-details")
async def get_application_autofill_info_endpoint(user_data=Depends(get_current_user)):
    return await get_application_autofill_info(user_data)


# Process a submitted application.
@router.post("/submit-application")
async def process_submitted_application_endpoint(
    form_data: dict = Body(...),
    db: Session = Depends(get_db),
    user_info=Depends(get_current_user),
):
    return await process_submitted_application(form_data, db, user_info)


# Get all applications for a specific form.
@router.get("/form/{form_id}", response_model=List[FormApplicationOut])
async def get_form_applications_endpoint(
    form_id: int, db: Session = Depends(get_db), user_data=Depends(get_current_user)
):
    try:
        applications = await get_form_applications(form_id, db, user_data)
        return applications
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Get all applications for the currently logged-in user.
@router.get("/user", response_model=List[UserApplicationOut])
async def get_user_applications_endpoint(
    db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)
):
    try:
        applications = await get_user_applications(db, user_data)
        return applications
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Get the current status of a submitted application.
@router.get("/{application_id}/status")
async def get_application_status_endpoint(
    application_id: int,
    db: Session = Depends(get_db),
    user_data=Depends(get_current_user),
):
    return await get_application_status(application_id, db, user_data)


# Get detailed information about a submitted application.
@router.get("/{application_id}")
async def get_application_details_endpoint(
    application_id: int,
    db: Session = Depends(get_db),
    user_data=Depends(get_current_user),
):
    return await get_application_details(application_id, db, user_data)


# Update status of an application.
@router.put("/{application_id}/status", response_model=ApplicationOut)
async def update_application_status_endpoint(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
):
    updated_application = await update_application_status(
        db, application_id, status_update
    )

    return updated_application


# Endorse an application.
@router.put("/{application_id}/endorse")
async def endorse_application_endpoint(
    application_id: int,
    db: Session = Depends(get_db),
    user_data=Depends(get_current_user),
):
    return await endorse_application(application_id, db, user_data)


# Withdraw endorsement from an application.
@router.put("/{application_id}/withdraw-endorsement")
async def withdraw_endorsement_endpoint(
    application_id: int,
    db: Session = Depends(get_db),
    user_data=Depends(get_current_user),
):
    return await withdraw_endorsement(application_id, db, user_data)


# Delete an application.
@router.delete("/{application_id}")
async def delete_application_endpoint(
    application_id: int,
    db: Session = Depends(get_db),
    user_data=Depends(get_current_user),
):
    return await delete_application(application_id, db, user_data)
