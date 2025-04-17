# backend/routers/recommendations.py

# Setup logger if not already done globally
import logging
from typing import List, Dict, Any  # Added Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status  # Removed Cookie
from sqlalchemy.orm import Session, joinedload

# Import the core logic function
from models.recommendation_engine.recommend import RecommendationContext
from schemas.clubs.clubs import ClubOut
from models.users.users_model import User
from utils.database_utils import get_db
# --- IMPORTANT: Import your actual get_current_user dependency ---
from utils.session_utils import get_current_user  # Assuming it's in utils.security, adjust path as needed


# Removed SESSION_COOKIE_NAME import as it's handled by get_current_user
logger = logging.getLogger(__name__)

def get_user_profile_with_clubs(user_id: str, db: Session) -> User | None:
     """Fetches user profile and eagerly loads their clubs."""
     logger.info(f"Fetching profile with clubs for user_id: {user_id}")
     try:
        # Eager load the 'clubs' relationship using joinedload
        user = db.query(User).\
            options(joinedload(User.clubs)).\
            filter(User.uid == user_id).\
            first()
        if not user:
             logger.warning(f"No user found with uid: {user_id} in get_user_profile_with_clubs")
        return user
     except Exception as e:
        # Log the specific exception
        logger.error(f"DB error in get_user_profile_with_clubs for user {user_id}: {e}", exc_info=True)
        return None


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"]
)

@router.get(
    "/clubs",
    response_model=List[ClubOut],
    summary="Get AI-based club recommendations for the current user (Strategy Pattern)",
    # ... (description remains the same)
)
async def get_club_recommendations_for_user_strategy(
    db: Session = Depends(get_db),
    # FastAPI awaits this dependency and injects the result (dict)
    current_user_data: Dict[str, Any] = Depends(get_current_user)
):
    # 1. Extract user_id from the dependency result
    user_id = current_user_data.get("uid")
    if not user_id or not isinstance(user_id, str):
        logger.error(f"Invalid user identifier from get_current_user: {user_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user identifier.")

    # 2. Fetch the full User database object using the user_id
    #    Call the synchronous function directly (no await needed here)
    user = get_user_profile_with_clubs(user_id, db)
    if not user:
        # Log the user_id that wasn't found
        logger.error(f"User profile not found in DB for uid: {user_id} (obtained from token/session)")
        # Return 404 Not Found, as the user from the token doesn't exist in our DB
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User profile for ID {user_id} not found.")

    # 3. Log user info (Now 'user' is the actual User object)
    logger.info(f"Generating recommendations for user: {user.uid} ({user.first_name})") # This should work now

    try:
        # 4. Use the Context with the fetched User object
        context = RecommendationContext(user, db)
        recommendations = await context.get_recommendations() # Returns List[Club]
        return recommendations # FastAPI converts Club objects to ClubResponse

    except TypeError as te:
         logger.error(f"Type error during recommendation context creation for user {user_id}: {te}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal configuration error.")
    except HTTPException as http_exc:
         raise http_exc # Re-raise known HTTP errors
    except Exception as e:
        logger.error(f"Unexpected error generating recommendations for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate recommendations due to an internal server error."
        )