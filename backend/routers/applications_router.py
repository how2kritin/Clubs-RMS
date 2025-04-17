from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body, Path
from sqlalchemy.orm import Session

from models.applications.applications_config import (get_application_autofill_info, process_submitted_application,
                                                     get_application_status, update_application_status,
                                                     endorse_application, withdraw_endorsement, delete_application,
                                                     get_application_details, get_user_applications,
                                                     get_form_applications, )
from models.users.users_config import inform_users
from models.users.users_model import User
from schemas.applications.applications import (ApplicationOut, ApplicationStatusUpdate, UserApplicationOut,
                                               FormApplicationOut, )
from utils.database_utils import get_db
from utils.session_utils import get_current_user

router = APIRouter(tags=["Applications"],
    responses={404: {"description": "Not found"}, 401: {"description": "Not authenticated"},
        403: {"description": "Forbidden - insufficient permissions"}, }, )


@router.get("/autofill-details", summary="Get Autofill Data",
    description="Retrieves user information to autofill application fields.",
    response_description="User data for application autofill", status_code=200, )
async def get_application_autofill_info_endpoint(user_data: dict = Depends(get_current_user), ):
    """
    Get user information that can be used to autofill fields in an application form.

    Returns basic user data like name, email, etc.
    """
    return await get_application_autofill_info(user_data)


@router.post("/submit-application", summary="Submit Application",
    description="Process a new application submission with responses to form questions.",
    response_description="The created application record", status_code=201, response_model=ApplicationOut, )
async def process_submitted_application_endpoint(form_data: dict = Body(..., example={"form_id": 123,
    "responses": [{"question_id": 1, "answer_text": "My response to question 1"},
        {"question_id": 2, "answer_text": "My response to question 2"}, ]},
    description="Application form data containing form ID and responses to questions", ), db: Session = Depends(get_db),
        user_info: dict = Depends(get_current_user), ):
    """
    Submit a new application for a recruitment form.

    - **form_data**: Contains the form ID and responses to questions
    - Authentication required: User must be logged in
    - Returns the created application with its ID and status
    """
    return await process_submitted_application(form_data, db, user_info)


@router.get("/form/{form_id}", response_model=List[FormApplicationOut], summary="Get Form Applications",
    description="Retrieves all applications for a specific form. Requires appropriate permissions.",
    response_description="List of applications for the specified form", )
async def get_form_applications_endpoint(
        form_id: int = Path(..., description="The ID of the form to retrieve applications for"),
        db: Session = Depends(get_db), user_data: dict = Depends(get_current_user), ):
    """
    Get all applications submitted for a specific form.

    - Authentication required: User must be logged in
    - Authorization required: User must be admin or member of the club that owns the form
    - Returns a list of applications with user information and responses
    """
    try:
        applications = await get_form_applications(form_id, db, user_data)
        return applications
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user", response_model=List[UserApplicationOut], summary="Get User Applications",
    description="Retrieves all applications submitted by the current user.",
    response_description="List of applications submitted by the current user", )
async def get_user_applications_endpoint(db: Session = Depends(get_db), user_data: dict = Depends(get_current_user), ):
    """
    Get all applications submitted by the currently logged-in user.

    - Authentication required: User must be logged in
    - Returns a list of the user's applications with submission details and status
    """
    try:
        applications = await get_user_applications(db, user_data)
        return applications
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{application_id}/status", summary="Get Application Status",
    description="Retrieves the current status of a specific application.",
    response_description="Current status of the application", )
async def get_application_status_endpoint(
        application_id: int = Path(..., description="The ID of the application to check status for"),
        db: Session = Depends(get_db), user_data: dict = Depends(get_current_user), ):
    """
    Check the current status of a specific application.

    - Authentication required: User must be logged in
    - Authorization required: Must be the applicant or a club member/admin
    - Returns the status and additional status-related information
    """
    return await get_application_status(application_id, db, user_data)


@router.get("/{application_id}", summary="Get Application Details",
    description="Retrieves detailed information about a specific application.",
    response_description="Detailed application information including responses", )
async def get_application_details_endpoint(
        application_id: int = Path(..., description="The ID of the application to retrieve"),
        db: Session = Depends(get_db), user_data: dict = Depends(get_current_user), ):
    """
    Get comprehensive details about a specific application.

    - Authentication required: User must be logged in
    - Authorization required: Must be the applicant or a club member/admin
    - Returns detailed application information including form responses
    """
    return await get_application_details(application_id, db, user_data)


@router.put("/{application_id}/status", response_model=ApplicationOut, summary="Update Application Status",
    description="Updates the status of an application (e.g., accepted, rejected).",
    response_description="The updated application record", )
async def update_application_status_endpoint(
        application_id: int = Path(..., description="The ID of the application to update"),
        status_update: ApplicationStatusUpdate = Body(..., description="New status details"),
        db: Session = Depends(get_db)):
    """
    Update the status of an application.

    - Authentication required: User must be logged in
    - Authorization required: Must be a club admin for the associated form
    - Email notification will be sent to the applicant
    - Returns the updated application with new status
    """
    updated_application, form = await update_application_status(db, application_id, status_update)

    user_id = updated_application.user_id
    user = db.query(User).filter(User.uid == user_id).first()
    subscribers = [user]

    inform_users(subscribers, "Application Status Update",
        f"Your application status for form {form.name} (club {form.club_id}) has been " + f"updated to {updated_application.status}.", )

    return updated_application


@router.put("/{application_id}/endorse", summary="Endorse Application",
    description="Adds an endorsement to an application by the current user.",
    response_description="Updated application with endorsement information", )
async def endorse_application_endpoint(
        application_id: int = Path(..., description="The ID of the application to endorse"),
        db: Session = Depends(get_db), user_data: dict = Depends(get_current_user), ):
    """
    Endorse a specific application.

    - Authentication required: User must be logged in
    - Authorization required: Must be a club member/admin for the associated form
    - A user can only endorse an application once
    - Returns the updated application with endorsement information
    """
    return await endorse_application(application_id, db, user_data)


@router.put("/{application_id}/withdraw-endorsement", summary="Withdraw Endorsement",
    description="Removes the current user's endorsement from an application.",
    response_description="Updated application with endorsement removed", )
async def withdraw_endorsement_endpoint(
        application_id: int = Path(..., description="The ID of the application to withdraw endorsement from"),
        db: Session = Depends(get_db), user_data: dict = Depends(get_current_user), ):
    """
    Withdraw your endorsement from an application.

    - Authentication required: User must be logged in
    - Authorization required: User must have previously endorsed the application
    - Returns the updated application with endorsement removed
    """
    return await withdraw_endorsement(application_id, db, user_data)


@router.delete("/{application_id}", summary="Delete Application", description="Permanently deletes an application.",
    response_description="Deletion confirmation", )
async def delete_application_endpoint(
        application_id: int = Path(..., description="The ID of the application to delete"),
        db: Session = Depends(get_db), user_data: dict = Depends(get_current_user), ):
    """
    Delete a specific application.

    - Authentication required: User must be logged in
    - Authorization required: Must be the applicant only
    - This action is irreversible
    - Returns confirmation of successful deletion
    """
    return await delete_application(application_id, db, user_data)
