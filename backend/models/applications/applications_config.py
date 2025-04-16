from fastapi import HTTPException, Depends
from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.applications.applications_model import Application, ApplicationStatus
from models.club_recruitment.club_recruitment_model import Form
from models.clubs.clubs_model import club_members
from schemas.applications.applications import ApplicationStatusUpdate
from utils.database_utils import get_db
from utils.session_utils import get_current_user


async def get_application_autofill_info():
    try:
        user_data = await get_current_user()

        return {"user_id": user_data["uid"], "first_name": user_data["first_name"], "last_name": user_data["last_name"],
                "email": user_data["email"], "roll_number": user_data["roll_number"], "hobbies": user_data["hobbies"],
                "skills": user_data["skills"], "batch": user_data["batch"]}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user information: {str(e)}")


async def process_submitted_application(form_data: dict, db: Session = Depends(get_db)):
    try:
        user_data = await get_current_user()
        user_id = user_data["uid"]

        form_id = form_data.get("form_id")
        if not form_id:
            raise HTTPException(status_code=400, detail="Form ID is required")

        # check if user has already applied to this form (if yes, do not proceed with this application)
        existing_application = db.query(Application).filter(Application.form_id == form_id,
                                                            Application.user_id == user_id).first()

        if existing_application:
            raise HTTPException(status_code=400, detail="You have already applied for this form")

        # create new application
        new_application = Application(form_id=form_id, user_id=user_id, status=ApplicationStatus.ongoing)

        db.add(new_application)
        db.commit()
        db.refresh(new_application)

        # process responses to questions
        responses_data = form_data.get("responses", [])
        for response_item in responses_data:
            from models.applications.applications_model import Response

            response = Response(application_id=new_application.id, question_id=response_item["question_id"],
                                answer_text=response_item["answer_text"])
            db.add(response)

        db.commit()

        return {"id": new_application.id, "status": new_application.status,
                "message": "Application submitted successfully"}

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process application: {str(e)}")


async def get_application_status(application_id: int, db: Session = Depends(get_db)):
    try:
        user_data = await get_current_user()
        user_id = user_data["uid"]

        # fetch application
        application = db.query(Application).filter(Application.id == application_id).first()

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        # check if the current user is the owner of the application or a member of the club the application is submitted to
        if application.user_id != user_id:
            form = db.query(Form).filter(Form.id == application.form_id).first()

            if not form:
                raise HTTPException(status_code=404,
                                    detail="Ran into an issue while fetching the form associated with this application")

            # check if the user is a member of the club
            club_membership = db.query(club_members).filter(
                and_(club_members.c.club_id == form.club_id, club_members.c.user_id == user_id)).first()

            if not club_membership:
                raise HTTPException(status_code=403, detail="You don't have permission to view this application")

        # return application status
        return {"id": application.id, "status": application.status.value, "submitted_at": application.submitted_at,
                "endorser_count": len(application.endorser_ids) if application.endorser_ids else 0}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch application status: {str(e)}")


async def update_application_status(db: Session, application_id: int, status_update: ApplicationStatusUpdate):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = status_update.status  # type: ignore

    db.commit()
    db.refresh(application)
    return application


# if the current user is a member of this club, they can endorse the application.
async def endorse_application(application_id: int, db: Session = Depends(get_db)):
    try:
        user_data = await get_current_user()
        user_id = user_data["uid"]

        # Fetch application
        application = db.query(Application).filter(Application.id == application_id).first()

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        form = db.query(Form).filter(Form.id == application.form_id).first()

        if not form:
            raise HTTPException(status_code=404, detail="Form associated with this application not found")

        club_id = form.club_id

        # check if user is a member of the club
        club_membership = db.query(club_members).filter(
            and_(club_members.c.club_id == club_id, club_members.c.user_id == user_id)).first()

        if not club_membership:
            raise HTTPException(status_code=403, detail="Only club members can endorse applications")

        # check if user has already endorsed this application
        if application.endorser_ids and user_id in application.endorser_ids:
            raise HTTPException(status_code=400, detail="You have already endorsed this application")

        # add user to endorsers list
        if application.endorser_ids:
            application.endorser_ids.append(user_id)
        else:
            application.endorser_ids = [user_id]

        db.commit()
        db.refresh(application)

        return {"id": application.id, "status": application.status.value,
                "endorser_count": len(application.endorser_ids) if application.endorser_ids else 0,
                "message": "Application endorsed successfully"}

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to endorse application: {str(e)}")


# Only the user that has submitted this application is allowed to delete it
async def delete_application(application_id: int, db: Session = Depends(get_db)):
    try:
        user_data = await get_current_user()
        user_id = user_data["uid"]

        application = db.query(Application).filter(Application.id == application_id).first()

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        # verify that only the user who submitted the application can delete it
        if application.user_id != user_id:
            raise HTTPException(status_code=403, detail="Only the user who submitted the application can delete it")

        db.delete(application)
        db.commit()

        return {"message": "Application deleted successfully", "id": application_id}

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete application: {str(e)}")
