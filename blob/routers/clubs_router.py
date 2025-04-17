from typing import List

from fastapi import APIRouter, status, Depends, Path
from sqlalchemy.orm import Session

from models.clubs.clubs_config import (
    fetch_club_by_id,
    fetch_info_about_all_clubs,
    is_subscribed,
    subscribe,
    unsubscribe,
)
from schemas.clubs.clubs import ClubOut
from utils.database_utils import get_db
from utils.session_utils import get_current_user

router = APIRouter(
    tags=["Clubs"],
    responses={
        404: {"description": "Club not found"},
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden - insufficient permissions"},
    },
)


@router.get(
    "/five_clubs",
    response_model=List[ClubOut],
    status_code=status.HTTP_200_OK,
    summary="Get All Clubs",
    description="Retrieves information about all clubs in the system.",
    response_description="List of all clubs with their details",
)
async def get_five_club_information(db: Session = Depends(get_db)):
    """
    Retrieve information about all clubs in the system.

    - No authentication required
    - Returns list of all clubs with their details including name, description, and contact information
    """
    clubs = await fetch_info_about_all_clubs(db)
    return []


@router.get(
    "/all_clubs",
    response_model=List[ClubOut],
    status_code=status.HTTP_200_OK,
    summary="Get All Clubs",
    description="Retrieves information about all clubs in the system.",
    response_description="List of all clubs with their details",
)
async def get_all_club_information(db: Session = Depends(get_db)):
    """
    Retrieve information about all clubs in the system.

    - No authentication required
    - Returns list of all clubs with their details including name, description, and contact information
    """
    return await fetch_info_about_all_clubs(db)


@router.get(
    "/{cid}",
    response_model=ClubOut,
    status_code=status.HTTP_200_OK,
    summary="Get Club by ID",
    description="Retrieves detailed information about a specific club by its ID.",
    response_description="Detailed information about the requested club",
    responses={404: {"description": "Club not found"}},
)
async def get_club_by_id(
    cid: str = Path(
        ...,
        description="The unique identifier of the club to retrieve",
        example="cs-club",
    ),
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific club.

    - No authentication required
    - Returns comprehensive details about the specified club including
      name, description, contact information, and membership details
    - Raises 404 error if the club doesn't exist
    """
    return await fetch_club_by_id(cid, db)


@router.get(
    "/is_subscribed/{cid}",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    summary="Check Subscription Status",
    description="Checks if the current user is subscribed to a specific club.",
    response_description="Boolean indicating whether the user is subscribed",
    responses={404: {"description": "Club not found"}},
)
def get_subscription_status(
    cid: str = Path(
        ...,
        description="The unique identifier of the club to check subscription status for",
        example="cs-club",
    ),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Check if the current user is subscribed to a specific club.

    - Authentication required: User must be logged in
    - Returns true if the user is subscribed, false otherwise
    - Raises 404 error if the club doesn't exist
    """
    return is_subscribed(cid, current_user["uid"], db)


@router.post(
    "/subscribe/{cid}",
    response_model=ClubOut,
    status_code=status.HTTP_200_OK,
    summary="Subscribe to Club",
    description="Subscribes the current user to notifications from a specific club.",
    response_description="Information about the club the user just subscribed to",
    responses={
        404: {"description": "Club not found"},
        400: {"description": "User is already subscribed to this club"},
    },
)
async def create_club_subscription(
    cid: str = Path(
        ...,
        description="The unique identifier of the club to subscribe to",
        example="cs-club",
    ),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Subscribe the current user to a specific club.

    Subscribing to a club allows the user to:
    - Receive notifications about club events and activities
    - Stay informed about recruitment drives and other announcements

    - Authentication required: User must be logged in
    - Returns information about the club after successful subscription
    - Raises 404 error if the club doesn't exist
    - Raises 400 error if the user is already subscribed
    """
    return await subscribe(cid, current_user["uid"], db)


@router.post(
    "/unsubscribe/{cid}",
    response_model=ClubOut,
    status_code=status.HTTP_200_OK,
    summary="Unsubscribe from Club",
    description="Unsubscribes the current user from notifications from a specific club.",
    response_description="Information about the club the user just unsubscribed from",
    responses={
        404: {"description": "Club not found"},
        400: {"description": "User is not subscribed to this club"},
    },
)
async def remove_club_subscription(
    cid: str = Path(
        ...,
        description="The unique identifier of the club to unsubscribe from",
        example="cs-club",
    ),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Unsubscribe the current user from a specific club.

    This will stop the user from receiving notifications about this club's activities.

    - Authentication required: User must be logged in
    - Returns information about the club after successful unsubscription
    - Raises 404 error if the club doesn't exist
    - Raises 400 error if the user is not currently subscribed
    """
    return await unsubscribe(cid, current_user["uid"], db)
