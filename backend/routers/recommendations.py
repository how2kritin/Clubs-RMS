# backend/routers/recommendations.py

from typing import List, Dict, Any # Added Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status # Removed Cookie
from sqlalchemy.orm import Session

from utils.database_utils import get_db
from schemas.clubs.clubs import ClubResponse
# Import the core logic function
from models.recommendation_engine.recommend import generate_club_recommendations
# --- IMPORTANT: Import your actual get_current_user dependency ---
from utils.session_utils import get_current_user # Assuming it's in utils.security, adjust path as needed
# Removed SESSION_COOKIE_NAME import as it's handled by get_current_user

# Setup logger if not already done globally
import logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"]
)

@router.get(
    "/clubs",
    response_model=List[ClubResponse],
    summary="Get AI-based club recommendations for the current user",
    description="Identifies the user via their authentication credentials (cookie/token), "
                "queries an AI model (Gemini) for relevant clubs based on their profile, "
                "and returns a list of recommended clubs."
)
async def get_club_recommendations_for_user(
    db: Session = Depends(get_db),
    # --- Use the existing dependency to get the authenticated user ---
    current_user: Dict[str, Any] = Depends(get_current_user) # Type hint might need adjustment based on what get_current_user returns
):
    """
    Provides personalized club recommendations based on the authenticated user's profile.
    """
    # --- Extract the user ID (uid) from the dependency result ---
    # Adjust the key 'uid' if get_current_user returns the ID under a different key
    user_id = current_user.get("uid")

    if not user_id:
        # This case should ideally be handled within get_current_user
        # by raising an HTTPException if authentication fails.
        # But as a safeguard:
        logger.error("Could not extract 'uid' from get_current_user result.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not identify user from authentication credentials."
        )

    # --- Check if uid is String (based on your User model) ---
    if not isinstance(user_id, str):
        logger.warning(f"User ID '{user_id}' from get_current_user is not a string. Attempting conversion.")
        try:
            user_id = str(user_id)
        except Exception:
             logger.error(f"Could not convert user ID '{user_id}' to string.")
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid user identifier format."
             )

    logger.info(f"Generating recommendations for user_id: {user_id}")

    try:
        # --- Pass the extracted user_id (as string) to the core logic ---
        recommendations = await generate_club_recommendations(user_id, db)
        return recommendations
    except HTTPException as http_exc:
         raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error generating recommendations for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate recommendations due to an internal error."
        )