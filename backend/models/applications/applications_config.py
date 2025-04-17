import datetime
from typing import Dict, Any, List

from fastapi import HTTPException, Depends
from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.applications.applications_model import Application, ApplicationStatus
from models.applications.applications_model import Response
from models.club_recruitment.club_recruitment_model import Form, Question
from models.clubs.clubs_model import club_members, Club
from models.users.users_config import is_member_of_club, is_admin_of_club
from models.users.users_model import User
from schemas.applications.applications import (
    ApplicationStatusUpdate,
    ApplicationDetailOut,
    ResponseOut,
)
from utils.database_utils import get_db
from utils.session_utils import get_current_user


async def get_application_autofill_info(user_data=Depends(get_current_user)):
    try:
        return {
            "user_id": user_data["uid"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "email": user_data["email"],
            "roll_number": user_data["roll_number"],
            "hobbies": user_data["hobbies"],
            "skills": user_data["skills"],
            "batch": user_data["batch"],
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve user information: {str(e)}"
        )


async def process_submitted_application(
    form_data: dict, db: Session = Depends(get_db), user_data=Depends(get_current_user)
):
    try:
        user_id = user_data["uid"]

        form_id = form_data.get("form_id")
        if not form_id:
            raise HTTPException(status_code=400, detail="Form ID is required")

        # check if user has already applied to this form (if yes, do not proceed with this application)
        existing_application = (
            db.query(Application)
            .filter(Application.form_id == form_id, Application.user_id == user_id)
            .first()
        )

        if existing_application:
            raise HTTPException(
                status_code=400, detail="You have already applied for this form"
            )

        # create new application
        new_application = Application(
            form_id=form_id, user_id=user_id, status=ApplicationStatus.ongoing
        )

        db.add(new_application)
        db.commit()
        db.refresh(new_application)

        # process responses to questions
        responses_data = form_data.get("responses", [])
        for response_item in responses_data:
            from models.applications.applications_model import Response

            response = Response(
                application_id=new_application.id,
                question_id=response_item["question_id"],
                answer_text=response_item["answer_text"],
            )
            db.add(response)

        db.commit()

        return {
            "id": new_application.id,
            "status": new_application.status,
            "message": "Application submitted successfully",
        }

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to process application: {str(e)}"
        )


# check if user has access to application (must've either submitted the application, or belong to the club)
async def _check_application_access(
    application_id: int, db: Session, user_data=Depends(get_current_user)
) -> Dict[str, Any]:
    user_id = user_data["uid"]

    # fetch application
    application = db.query(Application).filter(Application.id == application_id).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # check if the current user is the owner of the application or a member of the club the application is submitted to
    if application.user_id != user_id:
        form = db.query(Form).filter(Form.id == application.form_id).first()

        if not form:
            raise HTTPException(
                status_code=404,
                detail="Ran into an issue while fetching the form associated with this application",
            )

        # check if the user is a member of the club
        club_membership = is_member_of_club(user_id, form.club_id, db) or is_admin_of_club(user_id, form.club_id, db)

        if not club_membership:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to view this application",
            )

    return {"application": application, "user_id": user_id}


# get all details about the application
async def get_application_details(
    application_id: int,
    db: Session = Depends(get_db),
    user_data=Depends(get_current_user),
):
    try:
        result = await _check_application_access(application_id, db, user_data)
        application = result["application"]

        form = db.query(Form).filter(Form.id == application.form_id).first()
        if not form:
            raise HTTPException(
                status_code=404,
                detail="Form associated with this application not found",
            )

        user = db.query(User).filter(User.uid == application.user_id).first()
        user_email = user.email if user else None

        responses_data = []
        responses = (
            db.query(Response).filter(Response.application_id == application.id).all()
        )

        for response in responses:
            question = (
                db.query(Question).filter(Question.id == response.question_id).first()
            )

            response_out = ResponseOut(
                id=response.id,
                question_id=response.question_id,
                answer_text=response.answer_text,
                question_text=question.question_text if question else None,
                question_order=question.question_order if question else None,
            )
            responses_data.append(response_out)

        responses_data.sort(key=lambda x: (x.question_order or float("inf")))

        current_user_id = result["user_id"]

        if form.club_id:
            is_club_member = is_member_of_club(current_user_id, form.club_id, db) or is_admin_of_club(current_user_id, form.club_id, db)

        application_details = ApplicationDetailOut(
            id=application.id,
            form_id=application.form_id,
            user_id=application.user_id,
            form_name=form.name,
            club_id=form.club_id,
            submitted_at=application.submitted_at,
            status=application.status,
            responses=responses_data,
            endorser_ids=application.endorser_ids if application.endorser_ids else [],
            endorser_count=len(application.endorser_ids)
            if application.endorser_ids
            else 0,
            user_email=user_email,
            is_club_member=is_club_member,
        )

        return application_details

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch application details: {str(e)}"
        )


async def get_application_status(
    application_id: int,
    db: Session = Depends(get_db),
    user_data=Depends(get_current_user),
):
    try:
        result = await _check_application_access(application_id, db, user_data)
        application = result["application"]

        # return application status
        return {
            "id": application.id,
            "status": application.status.value,
            "submitted_at": application.submitted_at,
            "endorser_count": len(application.endorser_ids)
            if application.endorser_ids
            else 0,
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch application status: {str(e)}"
        )


async def update_application_status(
    db: Session, application_id: int, status_update: ApplicationStatusUpdate, user_data = Depends(get_current_user)
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    form_id = application.form_id
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    club_cid = form.club_id

    # only club admins should be able to update application status
    club_admin = is_admin_of_club(user_data.get("uid"), club_cid, db)

    if not club_admin:
        raise HTTPException(
            status_code=403, detail="Only club admins can update application status"
        )

    # if we are before the deadline, do not allow status update
    if form.deadline:
        # convert form.deadline to offset-aware if it's offset-naive
        deadline = form.deadline
        now = datetime.datetime.now(datetime.timezone.utc)

        # if deadline doesn't have timezone info, add UTC timezone
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=datetime.timezone.utc)

        if deadline > now:
            raise HTTPException(
                status_code=400,
                detail="Cannot update application status before the deadline",
            )

    application.status = status_update.status  # type: ignore
    if application.status == ApplicationStatus.accepted:  # type: ignore
        club = db.query(Club).filter(Club.cid == form.club_id).first()
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")

        user = db.query(User).filter(User.uid == application.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        club.members.append(user)

    db.commit()
    db.refresh(application)
    return application, form


# if the current user is a member of this club, they can endorse the application.
async def endorse_application(
    application_id: int,
    db: Session = Depends(get_db),
    user_data=Depends(get_current_user),
):
    try:
        user_id = user_data["uid"]

        # Fetch application
        application = (
            db.query(Application).filter(Application.id == application_id).first()
        )

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        form = db.query(Form).filter(Form.id == application.form_id).first()

        if not form:
            raise HTTPException(
                status_code=404,
                detail="Form associated with this application not found",
            )

        club_cid = form.club_id

        # check if user is a member of the club
        club_membership = is_member_of_club(user_id, club_cid, db) or is_admin_of_club(user_id, club_cid, db)

        if not club_membership:
            raise HTTPException(
                status_code=403, detail="Only club members and admins can endorse applications"
            )

        # check if user has already endorsed this application
        if application.endorser_ids and user_id in application.endorser_ids:
            raise HTTPException(
                status_code=400, detail="You have already endorsed this application"
            )

        # add user to endorsers list
        if application.endorser_ids:
            application.endorser_ids.append(user_id)
        else:
            application.endorser_ids = [user_id]

        db.commit()
        db.refresh(application)

        return {
            "id": application.id,
            "status": application.status.value,
            "endorser_count": len(application.endorser_ids)
            if application.endorser_ids
            else 0,
            "message": "Application endorsed successfully",
        }

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to endorse application: {str(e)}"
        )


async def withdraw_endorsement(
    application_id: int,
    db: Session = Depends(get_db),
    user_data=Depends(get_current_user),
):
    try:
        result = await _check_application_access(application_id, db, user_data)
        application = result["application"]
        user_id = result["user_id"]

        # check if the application is no longer in "ongoing" status
        if application.status != ApplicationStatus.ongoing:
            raise HTTPException(
                status_code=400,
                detail="Can only withdraw endorsements for ongoing applications",
            )

        # check if user has endorsed this application
        if user_id not in application.endorser_ids:
            raise HTTPException(
                status_code=400, detail="You have not endorsed this application"
            )

        # remove user from endorsers
        application.endorser_ids = [endorser_id for endorser_id in application.endorser_ids if endorser_id != user_id]

        db.commit()
        db.refresh(application)

        return {
            "id": application.id,
            "status": application.status.value,
            "endorser_count": len(application.endorser_ids)
            if application.endorser_ids
            else 0,
            "message": "Endorsement withdrawn successfully"
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to withdraw endorsement: {str(e)}"
        )


# only the user that has submitted this application is allowed to delete it
async def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    user_data=Depends(get_current_user),
):
    try:
        user_id = user_data["uid"]

        application = (
            db.query(Application).filter(Application.id == application_id).first()
        )

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        # verify that only the user who submitted the application can delete it
        if application.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Only the user who submitted the application can delete it",
            )

        db.delete(application)
        db.commit()

        return {"message": "Application deleted successfully", "id": application_id}

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to delete application: {str(e)}"
        )


async def get_form_applications(
    form_id: int, db: Session, user_data=Depends(get_current_user)
) -> List:
    user_uid = user_data.get("uid")
    if not user_uid:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # get the form to check club membership
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail=f"Form with ID {form_id} not found")

    club_cid = form.club_id

    # check if user is a club member or club admin
    club_membership = is_member_of_club(user_uid, club_cid, db) or is_admin_of_club(user_uid, club_cid, db)

    if not club_membership:
        raise HTTPException(
            status_code=403,
            detail="Only club members and admins can view all applications for a form",
        )

    # get all applications for this form
    applications = db.query(Application).filter(Application.form_id == form_id).all()

    # get user information for each application
    result = []
    for app in applications:
        user = db.query(User).filter(User.uid == app.user_id).first()
        user_name = f"{user.first_name} {user.last_name}" if user else "Unknown"

        app_dict = {
            "id": app.id,
            "user_id": app.user_id,
            "user_name": user_name,
            "user_email": user.email if user else None,
            "form_id": app.form_id,
            "form_name": form.name if form else None,
            "status": app.status.name,
            "endorser_ids": app.endorser_ids if app.endorser_ids else [],
            "endorser_count": len(app.endorser_ids) if app.endorser_ids else 0,
            "submitted_at": app.submitted_at.isoformat(),
        }
        result.append(app_dict)

    return result


async def get_user_applications(
    db: Session, user_data=Depends(get_current_user)
) -> List:
    user_uid = user_data.get("uid")
    if not user_uid:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # query applications with form and club information
    applications = db.query(Application).filter(Application.user_id == user_uid).all()

    result = []
    for app in applications:
        # get form information
        form = db.query(Form).filter(Form.id == app.form_id).first()
        if not form:
            continue

        # get club information
        club = db.query(Club).filter(Club.cid == form.club_id).first()
        if not club:
            continue

        app_dict = {
            "id": app.id,
            "form_id": app.form_id,
            "form_name": form.name,
            "club_id": form.club_id,
            "club_name": club.name if club else "Unknown",
            "status": app.status.name,
            "endorser_ids": app.endorser_ids if app.endorser_ids else [],
            "endorser_count": len(app.endorser_ids) if app.endorser_ids else 0,
            "submitted_at": app.submitted_at.isoformat(),
        }
        result.append(app_dict)

    return result

async def has_user_applied(form_id: int, db: Session, user_data=Depends(get_current_user)):
    user_id = user_data["uid"]
    existing_application = (
        db.query(Application)
        .filter(Application.form_id == form_id, Application.user_id == user_id)
        .first()
    )

    if existing_application:
        return {
            "has_applied": True,
            "application_id": existing_application.id,
            "status": existing_application.status
        }
    else:
        return {
            "has_applied": False,
            "application_id": None,
            "status": None
        }