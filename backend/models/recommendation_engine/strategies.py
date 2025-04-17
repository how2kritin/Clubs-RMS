# backend/models/recommendation_engine/strategies.py

import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from models.users.users_model import User
from models.clubs.clubs_model import Club, club_subscribers

logger = logging.getLogger(__name__)


class RecommendationStrategy(ABC):
    """
    Abstract base class for recommendation prompt generation strategies.
    """
    @abstractmethod
    def generate_prompt(self, user: User, all_clubs: List[Club], db: Session) -> Optional[str]:
        """
        Generates a prompt for the Gemini API based on the strategy.

        Args:
            user: The User object containing profile information.
            all_clubs: A list of all available Club objects.
            db: The database session (needed for some strategies like popularity).

        Returns:
            A string prompt for the Gemini API, or None if the strategy cannot generate a prompt
            (e.g., required data is missing, though selection logic should ideally prevent this).
        """
        pass

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
Return ONLY a comma-separated list of the Club IDs (e.g., 'coding,art,music') for the clubs you recommend.
Do not include any other text, explanation, headers, or formatting. Just the comma-separated IDs.
If no clubs seem like a good fit, return an empty string.
"""

class HobbiesSkillsStrategy(RecommendationStrategy):
    """
    Generates prompt based on user's hobbies and skills.
    """
    def generate_prompt(self, user: User, all_clubs: List[Club], db: Session) -> Optional[str]:
        # This strategy assumes it's selected *because* hobbies or skills exist.
        profile_lines = [f"User Profile for {user.first_name} (ID: {user.uid}):"]
        has_content = False
        if user.hobbies:
            profile_lines.append(f"- Hobbies: {user.hobbies}")
            has_content = True
        if user.skills: # Assuming skills is stored as JSON/dict or list-like string
            skills_str = str(user.skills) # Simple string conversion for prompt
            profile_lines.append(f"- Skills: {skills_str}")
            has_content = True

        if not has_content:
             logger.warning(f"HobbiesSkillsStrategy selected for user {user.uid} but no hobbies/skills found.")
             return None # Should not happen if selection logic is correct

        profile_str = "\n".join(profile_lines)
        clubs_str = self._format_club_list(all_clubs)
        instructions = self._get_base_instructions()

        prompt = f"""
Based on the following user profile (focusing on hobbies and skills) and the list of available clubs, recommend clubs the user might be interested in joining.

{profile_str}

{clubs_str}
{instructions}
"""
        logger.info(f"Using Hobbies/Skills strategy for user {user.uid}")
        return prompt.strip()


class CurrentClubsStrategy(RecommendationStrategy):
    """
    Generates prompt based on user's current club memberships.
    """
    def generate_prompt(self, user: User, all_clubs: List[Club], db: Session) -> Optional[str]:
        # Assumes user.clubs relationship is loaded or accessible
        current_clubs = user.clubs # Access the relationship defined by backref
        if not current_clubs:
            logger.warning(f"CurrentClubsStrategy selected for user {user.uid} but no current clubs found.")
            return None # Should not happen if selection logic is correct

        current_club_names = [c.name for c in current_clubs]
        profile_lines = [
            f"User Profile for {user.first_name} (ID: {user.uid}):",
            f"- Currently member of: {', '.join(current_club_names)}"
        ]
        profile_str = "\n".join(profile_lines)
        clubs_str = self._format_club_list(all_clubs)
        instructions = self._get_base_instructions()

        prompt = f"""
Based on the clubs the user is currently a member of, recommend other similar or complementary clubs from the available list.

{profile_str}

{clubs_str}
{instructions}
"""
        logger.info(f"Using Current Clubs strategy for user {user.uid}")
        return prompt.strip()


class PopularClubsStrategy(RecommendationStrategy):
    """
    Generates prompt aiming for generally popular or suitable clubs as a fallback.
    Optionally includes top N popular clubs in the prompt for context.
    """
    def generate_prompt(self, user: User, all_clubs: List[Club], db: Session) -> Optional[str]:
        # Fetch top N popular clubs based on member count
        top_n = 5
        try:
            popular_clubs_query = db.query(
                    Club.name, func.count(club_subscribers.c.user_id).label('subscriber_count')
                ).\
                join(club_subscribers, Club.cid == club_subscribers.c.club_id).\
                group_by(Club.cid).\
                order_by(desc('subscriber_count')).\
                limit(top_n)

            popular_clubs_list = [f"{name} ({count} members)" for name, count in popular_clubs_query.all()]
            print(f"Popular clubs: {popular_clubs_list}")
            popular_clubs_str = f"Some of the most popular clubs currently are: {', '.join(popular_clubs_list)}." if popular_clubs_list else ""

        except Exception as e:
            logger.error(f"Failed to query popular clubs: {e}", exc_info=True)
            popular_clubs_str = "Could not retrieve popularity data."


        profile_lines = [f"User Profile for {user.first_name} (ID: {user.uid}):"]
        if user.batch:
            profile_lines.append(f"- Batch: {user.batch}")
        profile_str = "\n".join(profile_lines)

        clubs_str = self._format_club_list(all_clubs)
        instructions = self._get_base_instructions()

        prompt = f"""
Recommend generally popular or suitable clubs for the following user from the available list. Think about clubs that might be broadly appealing or relevant given the user's batch (if provided), or clubs you have recommended in previous prompts.

{profile_str}

{popular_clubs_str}

{clubs_str}
{instructions}
"""
        logger.info(f"Using Popular Clubs (fallback) strategy for user {user.uid}")
        return prompt.strip()