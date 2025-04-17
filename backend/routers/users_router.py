"""
User authentication and profile management endpoints.

Some functionality adapted from https://github.com/IMS-IIITH/backend/blob/master/routers/users_router.py,
courtesy of https://github.com/bhavberi
"""

from os import getenv
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

from cas import CASClient
from fastapi import (
    APIRouter,
    Depends,
    Response,
    Request,
    status,
    Cookie,
    HTTPException,
    Path,
    Query,
    Body,
)
from sqlalchemy.orm import Session

from models.users.users_config import (
    get_clubs_by_user,
    is_admin_of_club,
    is_member_of_club,
    user_login_cas,
    user_logout,
)
from models.users.users_model import User
from schemas.clubs.clubs import ClubOut
from schemas.user.user import UserProfileUpdate
from utils.database_utils import get_db
from utils.session_utils import (
    SESSION_COOKIE_NAME,
    check_current_user,
    get_current_user,
)

# Configure CAS authentication client
CAS_SERVER_URL = getenv("CAS_SERVER_URL")
CAS_SERVICE_URL = f"{getenv('BASE_URL')}/{getenv('SUBPATH', 'api')}/user/login"
cas_client = CASClient(
    version=3, service_url=CAS_SERVICE_URL, server_url=CAS_SERVER_URL
)

router = APIRouter(
    tags=["User Authentication & Profile"],
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Get CAS Login URL",
    description="Returns the CAS login URL for the frontend to redirect the user.",
    response_description="CAS login URL to redirect the user to",
)
async def login_cas_redirect():
    """
    Get the CAS authentication URL for redirecting the user to the login page.

    This endpoint provides the URL that the frontend should use to redirect
    the user to the Central Authentication Service (CAS) login page.

    - No authentication required
    - Returns a URL to redirect the user to for CAS authentication
    """
    cas_login_url = cas_client.get_login_url()
    return {"loginUrl": cas_login_url}


@router.get(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Process CAS Login",
    description="Processes the ticket received from CAS after user authentication.",
    response_description="Authentication result with user data and session cookie",
    responses={
        400: {"description": "CAS ticket missing or invalid"},
        401: {"description": "Authentication failed"},
    },
)
async def login_cas(
    request: Request,
    response: Response,
    ticket: str = Query(None, description="CAS authentication ticket"),
    db: Session = Depends(get_db),
):
    """
    Process the CAS authentication ticket and create a user session.

    This endpoint is called after the user has authenticated with CAS and been
    redirected back to the application with a ticket parameter.

    The endpoint:
    1. Validates the CAS ticket with the CAS server
    2. Creates or updates the user in the database
    3. Creates a secure session for the authenticated user
    4. Sets a session cookie in the response

    - No authentication required (this is the authentication endpoint)
    - Requires a valid CAS ticket in the query parameters
    - Returns user information and sets a secure session cookie
    """
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


@router.get(
    "/user_info",
    status_code=status.HTTP_200_OK,
    summary="Get Current User Info",
    description="Retrieves information about the currently authenticated user.",
    response_description="User information for the authenticated user",
    response_model=Dict[str, Any],
)
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.

    This endpoint returns details about the logged-in user including:
    - User ID (uid)
    - Email address
    - Full name
    - Roll number
    - Profile information (if available)

    - Authentication required: User must be logged in
    - Returns user information from the session and database
    """
    return current_user


@router.get(
    "/user_role/{club_id}",
    status_code=status.HTTP_200_OK,
    summary="Get User Club Role",
    description="Checks if the current user is an admin or member of the specified club.",
    response_description="User's role information for the specified club",
)
async def get_user_role(
    club_id: str = Path(..., description="The unique identifier of the club"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Check the current user's role in a specific club.

    This endpoint determines if the authenticated user is:
    - An admin of the specified club
    - A member of the specified club

    This information is used for role-based access control throughout the application.

    - Authentication required: User must be logged in
    - Returns boolean values indicating admin and member status
    """
    return {
        "is_admin": is_admin_of_club(current_user["uid"], club_id, db),
        "is_member": is_member_of_club(current_user["uid"], club_id, db),
    }


@router.get(
    "/user_club_info",
    status_code=status.HTTP_200_OK,
    response_model=List[ClubOut],
    summary="Get User Club Memberships",
    description="Retrieves all clubs that the current user is a member or admin of.",
    response_description="List of clubs the user belongs to",
)
async def get_user_club_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all clubs that the current user is a member or admin of.

    This endpoint retrieves a list of clubs where the authenticated user has:
    - Admin privileges
    - Member status

    The result includes detailed information about each club including name,
    description, and other public details.

    - Authentication required: User must be logged in
    - Returns a list of clubs with detailed information
    """
    clubs = await get_clubs_by_user(current_user["uid"], db)
    return clubs


@router.get(
    "/is_authenticated",
    status_code=status.HTTP_200_OK,
    summary="Check Authentication Status",
    description="Checks if the current user has a valid authentication session.",
    response_description="Authentication status",
)
async def check_login(session: Optional[str] = Depends(check_current_user)):
    """
    Check if the current user is authenticated.

    This endpoint determines whether the current request includes a valid
    authentication session. It's useful for frontend applications to verify
    if the user is logged in without needing to fetch detailed user information.

    - No authentication required
    - Returns a boolean indicating if the user is authenticated
    """
    return {"authenticated": session is not None}


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout User",
    description="Logs out the current user by invalidating their session, and logs them out from CAS as well.",
    response_description="Logout confirmation",
)
async def logout(
    response: Response,
    db: Session = Depends(get_db),
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME),
):
    """
    Log out the current user.

    This endpoint:
    1. Invalidates the user's current session
    2. Clears the session cookie
    3. Prevents further authenticated access until the user logs in again

    - Authentication required: User must be logged in via session cookie
    - Returns confirmation of successful logout
    - Sets cookie to be cleared in the browser
    - Returns the URL to log out from CAS, with a redirection to the home page
    """
    await user_logout(response, session_id, db)
    cas_logout_url = cas_client.get_logout_url()
    encoded_frontend_url = quote_plus(getenv("FRONTEND_URL", "http://localhost:3000"))
    return {"logoutUrl": f"{cas_logout_url}?service={encoded_frontend_url}"}


@router.put(
    "/update_profile",
    status_code=status.HTTP_200_OK,
    summary="Update User Profile",
    description="Updates the profile information of the currently authenticated user.",
    response_description="Updated profile information",
    responses={
        400: {"description": "Invalid profile data"},
        401: {"description": "Not authenticated"},
        404: {"description": "User not found"},
        500: {"description": "Database error"},
    },
)
async def update_user_profile(
    profile_update: UserProfileUpdate = Body(
        ...,
        description="User profile data to update",
        example={
            "hobbies": "Reading, Photography, Hiking",
            "skills": ["Python", "React", "SQL"],
            "profile_picture": 2,
        },
    ),
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_current_user),
):
    """
    Update the profile information of the currently authenticated user.

    This endpoint allows users to modify their profile information including:
    - Hobbies (text description of interests)
    - Skills (list of technical or other skills)
    - Profile picture (index of selected avatar image)

    Field validation:
    - Hobbies: Optional text field
    - Skills: Optional list of strings
    - Profile picture: Optional integer from 0-4 representing avatar choices

    - Authentication required: User must be logged in
    - Returns confirmation of update and the modified profile fields
    """
    user_uid = current_user_data.get("uid")
    if not user_uid:
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
        db_user.habits.hobbies = update_data["hobbies"]
        updated = True
    if "skills" in update_data:
        db_user.habits.skills = update_data["skills"]
        updated = True
    if "profile_picture" in update_data:
        db_user.profile_picture = update_data["profile_picture"]
        updated = True

    if not updated:
        return {"message": "No updateable fields provided."}

    try:
        db.commit()
        db.refresh(db_user)  # Refresh to get the latest state from DB
    except ValueError as e:
        db.rollback()
        print(f"Immutable field update attempt failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        print(f"Error updating profile in DB: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update profile due to a server error.",
        )

    # Return success message and potentially the updated fields
    return {
        "message": "Profile updated successfully",
        "updated_profile": {
            "hobbies": db_user.habits.hobbies,
            "skills": db_user.habits.skills,
            "profile_picture": db_user.profile_picture,
        },
    }
