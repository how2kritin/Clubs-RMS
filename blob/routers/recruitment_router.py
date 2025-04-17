from typing import List

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status, Path, Query, Body
from sqlalchemy.orm import Session

from models.club_recruitment.club_recruitment_config import (create_form, delete_form, get_form_applicant_emails,
                                                             get_form_by_id, get_forms_by_club, update_form, )
from models.clubs.clubs_config import get_all_subscribers
from models.users.users_config import (inform_users, is_admin_of_club, is_member_of_club, )
from schemas.form.form import FormCreate, FormOut, FormUpdate
from utils.database_utils import get_db
from utils.session_utils import SESSION_COOKIE_NAME, get_current_user

router = APIRouter(tags=["Recruitment Forms"],
    responses={401: {"description": "Not authenticated"}, 403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "Resource not found"}, 400: {"description": "Bad request - validation error"}, }, )


@router.post("/forms", status_code=status.HTTP_201_CREATED, response_model=FormOut,
    summary="Create New Recruitment Form",
    description="Creates a new recruitment form for a club. Only club admins can create forms.",
    response_description="The newly created form with generated ID",
    responses={201: {"description": "Form created successfully"},
        403: {"description": "User is not an admin of the specified club"}})
async def create_new_form(form_data: FormCreate = Body(...,
    description="Form creation data including club ID, name, questions, and optional deadline",
    example={"club_id": "cs-club", "name": "Web Development Team Recruitment", "deadline": "2025-05-01T23:59:59Z",
        "questions": [{"question_text": "Why do you want to join our club?", "question_order": 1},
            {"question_text": "What relevant experience do you have?", "question_order": 2}]}),
        encrypted_session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME), db: Session = Depends(get_db), ):
    """
    Create a new recruitment form for a specific club.

    When a form is created:
    1. The system validates that the user is an admin of the specified club
    2. A notification is sent to all club subscribers about the new recruitment round
    3. The form becomes available for applicants to submit responses

    Form fields:
    - club_id: The ID of the club this form belongs to
    - name: The name/title of the recruitment round
    - deadline: Optional deadline for applications (ISO format timestamp)
    - questions: List of questions to include in the form

    - Authentication required: User must be logged in
    - Authorization required: User must be an admin of the specified club
    - Returns the newly created form details including the generated form ID
    """
    try:
        user = await get_current_user(encrypted_session_id, db)
        if not is_admin_of_club(user["uid"], form_data.club_id, db):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to create a form for this club.", )
        new_form = await create_form(db, form_data)

        subject = f"New Hiring Round Created: {new_form.name}"
        content = (
                f"A new hiring round has been created by the club {new_form.club_id}.\n" + "Head to clubs-plus-plus to see more!\n")

        subscribers = get_all_subscribers(db, new_form.club_id)  # type: ignore
        inform_users(subscribers, subject, content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return new_form


@router.get("/forms/club/{club_id}", response_model=List[FormOut], summary="Get Club Forms",
    description="Retrieves all recruitment forms associated with a specific club.",
    response_description="List of forms belonging to the specified club", )
async def get_all_forms(club_id: str = Path(..., description="The unique identifier of the club"),
        status_filter: str = Query(None, description="Optional filter for form status (active, closed, etc.)"),
        db: Session = Depends(get_db)):
    """
    Get all recruitment forms for a specific club.

    This endpoint retrieves all forms created by a club, optionally filtered by status.

    - No authentication required
    - Returns a list of forms with their details including questions
    - Can be filtered by status if query parameter is provided
    """
    try:
        forms = await get_forms_by_club(db, club_id)

        # Apply optional status filter if provided
        if status_filter:
            current_time = "2025-04-17T07:27:39Z"  # Using provided current time
            if status_filter == "active":
                forms = [f for f in forms if not f.deadline or f.deadline > current_time]
            elif status_filter == "closed":
                forms = [f for f in forms if f.deadline and f.deadline <= current_time]

        return forms
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/forms/{form_id}", response_model=FormOut, summary="Get Form Details",
    description="Retrieves detailed information about a specific recruitment form.",
    response_description="Complete form details including questions",
    responses={404: {"description": "Form not found"}})
async def get_form(form_id: int = Path(..., description="The unique identifier of the form to retrieve"),
        db: Session = Depends(get_db)):
    """
    Get detailed information about a specific recruitment form.

    This endpoint retrieves the complete details of a form including:
    - Basic form information (name, deadline, etc.)
    - All questions in the form with their order
    - Associated club information

    - No authentication required
    - Returns complete form details
    """
    try:
        form = await get_form_by_id(db, form_id)
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        return form
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/forms/{form_id}", response_model=FormOut, summary="Update Form",
    description="Updates an existing recruitment form. Only club admins or members can update forms.",
    response_description="The updated form details", responses={404: {"description": "Form not found"},
        403: {"description": "User is not authorized to update this form"}})
async def update_existing_form(form_id: int = Path(..., description="The unique identifier of the form to update"),
        form_data: FormUpdate = Body(..., description="Form update data including modified fields",
            example={"name": "Updated Web Development Team Recruitment", "deadline": "2025-05-15T23:59:59Z",
                "questions": [{"question_text": "Why do you want to join our club?", "question_order": 1},
                    {"question_text": "What relevant experience do you have?", "question_order": 2},
                    {"question_text": "New question added", "question_order": 3}]}),
        encrypted_session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME), db: Session = Depends(get_db), ):
    """
    Update an existing recruitment form.

    This endpoint allows club admins and members to modify a form by:
    - Updating the form name or deadline
    - Adding, removing, or modifying questions
    - Changing question order

    When a form is updated:
    - Subscribers of the club are notified about the changes
    - Existing applications to the form are preserved

    - Authentication required: User must be logged in
    - Authorization required: User must be an admin or member of the club that owns the form
    - Returns the updated form details
    """
    try:
        user = await get_current_user(encrypted_session_id, db)
        form = await get_form_by_id(db, form_id)
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        if not (is_member_of_club(user["uid"], form.club_id, db)  # type: ignore
                or is_admin_of_club(user["uid"], form.club_id, db)  # type: ignore
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this form.", )

        updated_form = await update_form(db, form_id, form_data)

        subject = f"Hiring Round Updated: {updated_form.name}"
        content = (
                f"Hiring round {updated_form.name} has been updated by the club {updated_form.club_id}.\n" + "Head to clubs-plus-plus to see more!\n")

        subscribers = get_all_subscribers(db, updated_form.club_id)  # type: ignore
        inform_users(subscribers, subject, content)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return updated_form


@router.delete("/forms/{form_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Form",
    description="Permanently deletes a recruitment form. Only club admins can delete forms.",
    response_description="No content returned on successful deletion",
    responses={404: {"description": "Form not found"},
        403: {"description": "User is not authorized to delete this form"}})
async def delete_existing_form(form_id: int = Path(..., description="The unique identifier of the form to delete"),
        encrypted_session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME), db: Session = Depends(get_db), ):
    """
    Delete a recruitment form permanently.

    When a form is deleted:
    - All associated applications are also deleted
    - Club subscribers are notified about the deletion
    - The form is no longer available for applications

    This operation is irreversible.

    - Authentication required: User must be logged in
    - Authorization required: User must be an admin of the club that owns the form
    - Returns no content on successful deletion
    """
    try:
        user = await get_current_user(encrypted_session_id, db)
        form = await get_form_by_id(db, form_id)
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        if not is_admin_of_club(user["uid"], form.club_id, db):  # type: ignore
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delete this form.", )
        subscribers = get_all_subscribers(db, form.club_id)  # type: ignore

        await delete_form(db, form_id)

        subject = f"Hiring Round Deleted: {form.name}"
        content = (f"Hiring round {form.name} has been deleted by the club {form.club_id}.\n")

        inform_users(subscribers, subject, content)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/forms/{form_id}/applicants/emails", response_model=List[str], summary="Get Applicant Emails",
    description="Retrieves a list of email addresses for all applicants who applied to a specific form. Only club members or admins can do this.",
    response_description="List of applicant email addresses", responses={404: {"description": "Form not found"},
        403: {"description": "User is not authorized to view applicant emails"}})
async def get_applicants_emails(form_id: int = Path(..., description="The unique identifier of the form"),
        encrypted_session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME), db: Session = Depends(get_db), ):
    """
    Get email addresses of all applicants who applied to a specific form.

    This endpoint is useful for:
    - Sending bulk communications to applicants
    - Exporting application data for external processing

    - Authentication required: User must be logged in
    - Authorization required: User must be an admin or member of the club that owns the form
    - Returns a list of email addresses
    """
    try:
        # Get current user for authorization
        user = await get_current_user(encrypted_session_id, db)

        # Get the form to check club ownership
        form = await get_form_by_id(db, form_id)
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        # Verify the user is authorized to view applicant emails
        if not (is_member_of_club(user["uid"], form.club_id, db)  # type: ignore
                or is_admin_of_club(user["uid"], form.club_id, db)  # type: ignore
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view applicant emails for this form.", )

        emails = await get_form_applicant_emails(db, form_id)
        return emails
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
