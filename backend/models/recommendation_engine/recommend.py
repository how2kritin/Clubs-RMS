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

from .strategies import (
    RecommendationStrategy,
    HobbiesSkillsStrategy,
    CurrentClubsStrategy,
    PopularClubsStrategy,
)

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
    if not gemini_model:
        logger.error("Gemini model not initialized. Cannot get recommendations.")
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
        logger.info(f"Parsed recommended CIDs: {recommended_cids}")
    except Exception as e:
        logger.error(
            f"Error calling Gemini API or parsing response: {e}", exc_info=True
        )
        if "response" in locals() and hasattr(response, "prompt_feedback"):
            logger.error(f"Gemini Prompt Feedback: {response.prompt_feedback}")
        recommended_cids = []
    return recommended_cids


logger = logging.getLogger(__name__)


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
        # Check 1: Hobbies or Skills present?
        # Ensure skills check is meaningful (e.g., not None, not empty dict/list if applicable)
        if self._user.habits.hobbies or (
            self._user.habits.skills
            and self._user.habits.skills != {}
            and self._user.habits.skills != []
        ):
            logger.debug(f"Selecting HobbiesSkillsStrategy for user {self._user.uid}")
            return HobbiesSkillsStrategy()

        # Check 2: Current Clubs present?
        # Accessing user.clubs might trigger a lazy load if not eager loaded before.
        # It's better to eager load when fetching the user initially.
        if self._user.clubs:
            logger.debug(f"Selecting CurrentClubsStrategy for user {self._user.uid}")
            return CurrentClubsStrategy()

        # Fallback: Popular Clubs
        logger.debug(f"Selecting PopularClubsStrategy for user {self._user.uid}")
        return PopularClubsStrategy()

    def _fetch_all_clubs(self) -> List[Club]:
        """Fetches all clubs from the database."""
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
        Orchestrates the recommendation process using the selected strategy.
        """
        all_clubs = self._fetch_all_clubs()
        if not all_clubs:
            return []

        prompt = self._strategy.generate_prompt(self._user, all_clubs, self._db)

        if not prompt:
            logger.warning(
                f"Selected strategy {self._strategy.__class__.__name__} failed to generate a prompt for user {self._user.uid}."
            )
            return []

        logger.debug(
            f"Generated Prompt for Gemini (User: {self._user.uid}, Strategy: {self._strategy.__class__.__name__}):\n{prompt}"
        )

        recommended_cids = await get_recommendations_from_gemini(prompt)
        if not recommended_cids:
            logger.info(
                f"No recommendations received from Gemini for user {self._user.uid}."
            )
            return []

        try:
            valid_cids = [str(cid) for cid in recommended_cids]
            recommended_clubs_query = self._db.query(Club).filter(
                Club.cid.in_(valid_cids)
            )
            recommended_clubs_list = recommended_clubs_query.all()

            recommended_clubs_dict = {club.cid: club for club in recommended_clubs_list}
            ordered_recommended_clubs = [
                recommended_clubs_dict[cid]
                for cid in valid_cids
                if cid in recommended_clubs_dict
            ]

            logger.info(
                f"Returning {len(ordered_recommended_clubs)} recommendations for user {self._user.uid} using {self._strategy.__class__.__name__}."
            )
            return ordered_recommended_clubs

        except SQLAlchemyError as e:
            logger.error(
                f"Database error fetching recommended clubs by CID: {e}", exc_info=True
            )
            return []
        except Exception as e:
            logger.error(
                f"Unexpected error fetching recommended clubs: {e}", exc_info=True
            )
            return []

