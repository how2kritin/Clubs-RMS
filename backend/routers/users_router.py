# user_router.py
"""
Some users functionality copied over from
https://github.com/IMS-IIITH/backend/blob/master/routers/users_router.py,
courtesy of https://github.com/bhavberi
"""

from os import getenv
from typing import List

from cas import CASClient
from fastapi import (
    APIRouter,
    Depends,
    Response,
    Request,
    status,
    Cookie,
    HTTPException,
)  # Added HTTPException
from sqlalchemy.orm import Session

from models.users.users_config import (
    get_clubs_by_user,
    is_admin_of_club,
    user_login_cas,
    user_logout,
)
from models.users.users_model import User  # Import User model
from schemas.clubs.clubs import ClubOut
from schemas.user.user import UserProfileUpdate
from utils.database_utils import get_db
from utils.session_utils import (
    SESSION_COOKIE_NAME,
    check_current_user,
    get_current_user,
)  # Added invalidate_session for logout

CAS_SERVER_URL = getenv("CAS_SERVER_URL")
CAS_SERVICE_URL = f"{getenv('BASE_URL')}/{getenv('SUBPATH', 'api')}/user/login"  # Ensure SUBPATH is included if used

cas_client = CASClient(
    version=3, service_url=CAS_SERVICE_URL, server_url=CAS_SERVER_URL
)

router = APIRouter()


# --- Routes ---


# User Login via CAS. Returns the URL for the frontend to redirect to CAS login
@router.post("/login", status_code=status.HTTP_200_OK)
async def login_cas_redirect():
    cas_login_url = cas_client.get_login_url()
    return {"loginUrl": cas_login_url}


# User Login via CAS. Process the ticket received from CAS
@router.get("/login", status_code=status.HTTP_200_OK)
async def login_cas(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    ticket = request.query_params.get("ticket")
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CAS ticket not found in query parameters",
        )

    user_agent = request.headers.get("user-agent", "")
    ip_address = request.client.host if request.client else None
    return await user_login_cas(
        response, ticket, user_agent, ip_address, cas_client, db
    )


# Fetch the info of the currently logged-in user
@router.get("/user_info", status_code=status.HTTP_200_OK)
async def get_user_info(current_user: dict = Depends(get_current_user)):
    return current_user


@router.get("/user_admin/{club_id}", status_code=status.HTTP_200_OK)
async def user_is_admin(
    club_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"is_admin": is_admin_of_club(current_user["uid"], club_id, db)}


@router.get(
    "/user_club_info", status_code=status.HTTP_200_OK, response_model=List[ClubOut]
)
async def get_user_club_info(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    clubs = await get_clubs_by_user(current_user["uid"], db)
    return clubs


# Check if a user is logged in
@router.get("/is_authenticated", status_code=status.HTTP_200_OK)
async def check_login(session: str = Depends(check_current_user)):
    return {"authenticated": session is not None}


# User Logout
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    db: Session = Depends(get_db),
    session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME),
):
    return await user_logout(response, session_id, db)


# --- NEW: Update User Profile Endpoint ---
@router.put("/update_profile", status_code=status.HTTP_200_OK)
async def update_user_profile(
    profile_update: UserProfileUpdate,  # Use Pydantic model for validation
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_current_user),
    # Authenticate and get user UID
):
    user_uid = current_user_data.get("uid")
    if not user_uid:
        # ? This check is slightly redundant due to Depends(get_current_user)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not identify user"
        )

    # Fetch the user object from DB
    db_user = db.query(User).filter(User.uid == user_uid).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get the data provided in the request body, excluding fields not set by the client
    update_data = profile_update.model_dump(exclude_unset=True)

    updated = False
    # Update only the allowed fields if they are present in the update_data
    if "hobbies" in update_data:
        db_user.hobbies = update_data["hobbies"]
        updated = True
    if "skills" in update_data:
        db_user.skills = update_data["skills"]
        updated = True
    if "profile_picture" in update_data:
        db_user.profile_picture = update_data["profile_picture"]
        updated = True

    if not updated:
        # If no relevant fields were sent in the request body
        return {"message": "No updateable fields provided."}

    try:
        db.commit()
        db.refresh(db_user)  # Refresh to get the latest state from DB
    except ValueError as e:
        # Catch the specific error raised by the immutable field check
        db.rollback()
        print(f"Immutable field update attempt failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        print(f"Error updating profile in DB: {e}")  # Log the error server-side
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update profile due to a server error.",
        )

    # Return success message and potentially the updated fields
    return {
        "message": "Profile updated successfully",
        "updated_profile": {
            "hobbies": db_user.hobbies,
            "skills": db_user.skills,
            "profile_picture": db_user.profile_picture,
        },
    }
