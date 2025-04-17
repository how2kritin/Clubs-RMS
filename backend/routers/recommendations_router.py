# backend/routers/recommendations.py

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from models.recommendation_engine.recommend import RecommendationContext
from models.users.users_model import User
from schemas.clubs.clubs import ClubOut
from utils.database_utils import get_db
from utils.session_utils import get_current_user

logger = logging.getLogger(__name__)


def get_user_profile_with_clubs(user_id: str, db: Session) -> User | None:
    """Fetches user profile and eagerly loads their clubs."""
    logger.info(f"Fetching profile with clubs for user_id: {user_id}")
    try:
        user = db.query(User).options(joinedload(User.clubs)).filter(User.uid == user_id).first()
        if not user:
            logger.warning(f"No user found with uid: {user_id} in get_user_profile_with_clubs")
        return user
    except Exception as e:
        logger.error(f"DB error in get_user_profile_with_clubs for user {user_id}: {e}", exc_info=True)
        return None


router = APIRouter(prefix="/recommendations", tags=["Recommendations"],
    responses={401: {"description": "Not authenticated"}, 404: {"description": "User profile not found"},
        500: {"description": "Internal server error"}, }, )


@router.get("/clubs", response_model=List[ClubOut], summary="Get AI-based Club Recommendations",
    description="Provides personalized club recommendations for the authenticated user based on their profile and interests.",
    response_description="List of recommended clubs ordered by relevance", )
async def get_club_recommendations_for_user_strategy(db: Session = Depends(get_db),
        current_user_data: Dict[str, Any] = Depends(get_current_user)):
    """
    Get personalized club recommendations using a strategy pattern.

    This endpoint analyzes the user's profile including their interests, skills,
    and current club memberships to generate tailored recommendations for clubs
    they might be interested in joining.

    The recommendation algorithm considers:
    - User's listed skills and interests
    - Current club memberships
    - Academic background
    - Similar users' preferences

    - Authentication required: User must be logged in
    - Returns a list of clubs ordered by relevance to the user
    """
    user_id = current_user_data.get("uid")
    if not user_id or not isinstance(user_id, str):
        logger.error(f"Invalid user identifier from get_current_user: {user_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user identifier.")

    user = get_user_profile_with_clubs(user_id, db)
    if not user:
        logger.error(f"User profile not found in DB for uid: {user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User profile for ID {user_id} not found.")

    logger.info(f"Generating recommendations for user: {user.uid} ({user.first_name})")

    try:
        context = RecommendationContext(user, db)
        recommendations = await context.get_recommendations()
        return recommendations

    except TypeError as te:
        logger.error(f"Type error during recommendation context creation for user {user_id}: {te}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal configuration error.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error generating recommendations for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate recommendations due to an internal server error.")
