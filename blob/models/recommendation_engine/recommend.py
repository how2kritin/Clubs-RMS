# backend/models/recommendation_engine/recommend.py

import os
import logging
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.users.users_model import User
from models.clubs.clubs_model import Club
from schemas.clubs.clubs import ClubOut

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "envs", ".env")
load_dotenv(dotenv_path=dotenv_path)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_model = None
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("Gemini API configured successfully.")
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")


async def get_recommendations_from_gemini(prompt: str) -> List[str]:
    """Calls the Gemini API and returns a list of recommended CIDs."""
    if not gemini_model:
        logger.error("Gemini model not initialized. Cannot get recommendations.")
        return []
    if not prompt:
        logger.warning("get_recommendations_from_gemini called with empty prompt.")
        return []

    recommended_cids = []
    try:
        logger.info("Sending request to Gemini API...")
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
        ]
        response = await gemini_model.generate_content_async(
            prompt, safety_settings=safety_settings
        )
        logger.debug(f"Raw Gemini Response Text: '{response.text}'")
        raw_cids = response.text.strip()
        if raw_cids:
            recommended_cids = [
                cid.strip() for cid in raw_cids.split(",") if cid.strip()
            ]
        logger.info(f"Parsed recommended CIDs from Gemini: {recommended_cids}")
    except Exception as e:
        logger.error(
            f"Error calling Gemini API or parsing response: {e}", exc_info=True
        )
        if "response" in locals() and hasattr(response, "prompt_feedback"):
            logger.error(f"Gemini Prompt Feedback: {response.prompt_feedback}")
        recommended_cids = []
    return recommended_cids


from .strategies import (
    RecommendationStrategy,
    HobbiesSkillsStrategy,
    CurrentClubsStrategy,
    PopularClubsStrategy,
)


class RecommendationContext:
    """
    Context class to manage and execute recommendation strategies.
    """

    def __init__(self, user: User, db: Session):
        if not isinstance(user, User):
            raise TypeError("RecommendationContext requires a valid User object.")
        self._user = user
        self._db = db
        self._strategy: RecommendationStrategy = self._select_strategy()
        self._all_clubs: Optional[List[Club]] = None

    def _select_strategy(self) -> RecommendationStrategy:
        """Selects the appropriate strategy based on user data."""
        if self._user.habits.hobbies or (
            self._user.habits.skills
            and self._user.habits.skills != {}
            and self._user.habits.skills != []
        ):
            logger.debug(f"Selecting HobbiesSkillsStrategy for user {self._user.uid}")
            return HobbiesSkillsStrategy()

        try:
            if self._user.clubs:
                logger.debug(
                    f"Selecting CurrentClubsStrategy for user {self._user.uid}"
                )
                return CurrentClubsStrategy()
        except SQLAlchemyError as e:
            logger.error(
                f"Database error accessing user.clubs for user {self._user.uid}: {e}. Falling back."
            )

        logger.debug(f"Selecting PopularClubsStrategy for user {self._user.uid}")
        return PopularClubsStrategy()

    def _fetch_all_clubs(self) -> List[Club]:
        """Fetches all active/relevant clubs from the database."""
        if self._all_clubs is None:
            try:
                self._all_clubs = self._db.query(Club).order_by(Club.name).all()
                if not self._all_clubs:
                    logger.warning("No clubs found in the database.")
                    self._all_clubs = []
            except SQLAlchemyError as e:
                logger.error(f"Database error fetching all clubs: {e}", exc_info=True)
                self._all_clubs = []
        return self._all_clubs

    async def get_recommendations(self) -> List[Club]:
        """
        Orchestrates the recommendation process by delegating to the selected strategy.
        """
        all_clubs = self._fetch_all_clubs()
        if not all_clubs and not isinstance(self._strategy, PopularClubsStrategy):
            logger.warning(
                f"No clubs available to recommend for user {self._user.uid}."
            )
            return []

        logger.info(
            f"Using strategy {self._strategy.__class__.__name__} for user {self._user.uid}."
        )

        try:
            recommended_clubs: List[Club] = await self._strategy.get_recommendations(
                self._user, all_clubs, self._db
            )

            logger.info(
                f"Strategy {self._strategy.__class__.__name__} returned {len(recommended_clubs)} recommendations for user {self._user.uid}."
            )
            if not isinstance(recommended_clubs, list) or not all(
                isinstance(c, Club) for c in recommended_clubs
            ):
                logger.error(
                    f"Strategy {self._strategy.__class__.__name__} did not return a valid List[Club]. Returning empty list."
                )
                return []

            return recommended_clubs

        except Exception as e:
            logger.error(
                f"Error executing strategy {self._strategy.__class__.__name__} for user {self._user.uid}: {e}",
                exc_info=True,
            )
            return []
