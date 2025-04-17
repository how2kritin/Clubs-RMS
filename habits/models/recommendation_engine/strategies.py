# backend/models/recommendation_engine/strategies.py

import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Set

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, select
from sqlalchemy.exc import SQLAlchemyError

from models.users.users_model import User
from models.clubs.clubs_model import Club, club_subscribers
from .recommend import get_recommendations_from_gemini

logger = logging.getLogger(__name__)


class RecommendationStrategy(ABC):
    """
    Abstract base class for recommendation strategies.
    Each strategy is responsible for generating the final list of recommended clubs.
    """

    @abstractmethod
    async def get_recommendations(
        self, user: User, all_clubs: List[Club], db: Session
    ) -> List[Club]:
        """
        Generates a list of recommended Club objects based on the strategy.

        Args:
            user: The User object containing profile information.
            all_clubs: A list of all available Club objects (can be used for prompt context or filtering).
            db: The database session.

        Returns:
            A list of recommended Club objects, excluding clubs the user is already a member of.
        """
        pass

    def _get_user_member_cids(self, user: User) -> Set[str]:
        """Helper to get the CIDs of clubs the user is already a member of."""
        return {club.cid for club in user.clubs} if user.clubs else set()

    def _format_club_list(self, all_clubs: List[Club]) -> str:
        """Helper to format the list of available clubs for the prompt."""
        clubs_lines = ["Available Clubs (Name - ID):"]
        for club in all_clubs:
            clubs_lines.append(f"- {club.name} - {club.cid}")
        return "\n".join(clubs_lines)

    def _get_base_instructions(self) -> str:
        """Helper to get the standard instructions for Gemini."""
        return """
Instructions:
Return ONLY a comma-separated list of the Club IDs (e.g., 'club-101,club-105,club-110') for the clubs you recommend based *only* on the information provided. Limit to a maximum of 5 recommendations.
Do not include any other text, explanation, headers, or formatting. Just the comma-separated IDs.
If no clubs seem like a good fit based on the criteria, return an empty string.
"""

class PopularClubsStrategy(RecommendationStrategy):
    """
    Recommends the top N most popular clubs (by subscriber count), excluding those the user is already in.
    Does NOT use an LLM.
    """

    async def get_recommendations(
        self, user: User, all_clubs: List[Club], db: Session
    ) -> List[Club]:
        logger.info(f"Using Popular Clubs (fallback) strategy for user {user.uid}")
        top_n = 5
        user_member_cids = self._get_user_member_cids(user)

        try:
            popular_clubs_query = (
                select(Club)
                .join(club_subscribers, Club.cid == club_subscribers.c.club_id)
                .group_by(Club.cid)
                .order_by(desc(func.count(club_subscribers.c.user_id)))
                .limit(top_n * 2)
            )
            popular_clubs_results = db.execute(popular_clubs_query).scalars().all()

            recommended_clubs = [
                club
                for club in popular_clubs_results
                if club.cid not in user_member_cids
            ]

            final_recommendations = recommended_clubs[:top_n]

            logger.info(
                f"PopularClubsStrategy for user {user.uid} found {len(popular_clubs_results)} popular, returning {len(final_recommendations)} after filtering."
            )
            return final_recommendations

        except SQLAlchemyError as e:
            logger.error(
                f"Database error fetching popular clubs for user {user.uid}: {e}",
                exc_info=True,
            )
            return []
        except Exception as e:
            logger.error(
                f"Unexpected error in PopularClubsStrategy for user {user.uid}: {e}",
                exc_info=True,
            )
            return []
