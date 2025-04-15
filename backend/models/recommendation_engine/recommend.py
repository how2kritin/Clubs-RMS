# backend/models/recommendation_engine/recommend.py

import os
import logging
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError # Import specific DB errors

# Import your actual models and schemas
from models.users.users_model import User # Import your actual User model
from models.clubs.clubs_model import Club
from schemas.clubs.clubs import ClubResponse

# --- Environment Variable Loading & Gemini Config (Keep as before) ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'envs', '.env')
load_dotenv(dotenv_path=dotenv_path)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_model = None
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("Gemini API configured successfully.")
        gemini_model = genai.GenerativeModel('gemini-1.5-flash') # Or your preferred model
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
# --- End Gemini Config ---


# --- Function to fetch User Data ---
# Ensure this uses your actual User model and expects a string uid
def get_user_profile(user_id: str, db: Session) -> Optional[User]:
    """Fetches user profile data using the string user ID."""
    logger.info(f"Fetching profile for user_id: {user_id}")
    try:
        user = db.query(User).filter(User.uid == user_id).first()
        if not user:
            logger.warning(f"No user found with uid: {user_id}")
            return None
        # Eager load related data if needed for the prompt (e.g., hobbies, interests)
        # This depends on how your User model relationships are set up.
        # Example: options(joinedload(User.hobbies_relation))
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching profile for user {user_id}: {e}", exc_info=True)
        # Re-raise or handle appropriately - maybe return None or raise custom exception
        return None # Returning None for now

# --- Function to generate prompt (Adjust field access based on your User model) ---
def create_recommendation_prompt(user_profile: User, all_clubs: List[Club]) -> str:
    """Creates the prompt for the Gemini API using the User model."""

    # --- Access fields directly from the SQLAlchemy User object ---
    profile_lines = [f"User Profile for {user_profile.first_name} {user_profile.last_name} (ID: {user_profile.uid}):"]

    # Add fields IF they exist on your User model. Add more as needed.
    if hasattr(user_profile, 'hobbies') and user_profile.hobbies:
        profile_lines.append(f"- Hobbies: {user_profile.hobbies}") # Assuming 'hobbies' is a field
    if hasattr(user_profile, 'interests') and user_profile.interests:
        profile_lines.append(f"- Interests: {user_profile.interests}") # Assuming 'interests' is a field
    # Add current clubs if you have that relationship defined
    # if hasattr(user_profile, 'current_clubs_relation') and user_profile.current_clubs_relation:
    #     club_names = [c.name for c in user_profile.current_clubs_relation]
    #     profile_lines.append(f"- Currently in Clubs: {', '.join(club_names)}")
    # Add other relevant fields like 'roll_number' if useful for context?
    # profile_lines.append(f"- Roll Number: {user_profile.roll_number}")

    profile_str = "\n".join(profile_lines)

    clubs_lines = ["Available Clubs (Name - ID):"]
    for club in all_clubs:
        clubs_lines.append(f"- {club.name} - {club.cid}") # Assuming Club model has 'name' and 'cid'
    clubs_str = "\n".join(clubs_lines)

    prompt = f"""
Based on the following user profile and list of available clubs, recommend clubs the user might be interested in joining.

{profile_str}

{clubs_str}

Instructions:
Return ONLY a comma-separated list of the Club IDs (e.g., 'coding,art,music') for the clubs you recommend.
Do not include any other text, explanation, headers, or formatting. Just the comma-separated IDs.
If no clubs seem like a good fit, return an empty string.
"""
    return prompt.strip()

# --- Function to call Gemini and parse response (Keep as before) ---
async def get_recommendations_from_gemini(prompt: str) -> List[str]:
    # (Implementation from previous answer - no changes needed here)
    if not gemini_model:
        logger.error("Gemini model not initialized. Cannot get recommendations.")
        return []
    recommended_cids = []
    try:
        logger.info("Sending request to Gemini API...")
        safety_settings=[ # Adjust safety settings as needed
             {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
             {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
             {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
             {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        response = await gemini_model.generate_content_async(prompt, safety_settings=safety_settings)
        logger.debug(f"Raw Gemini Response Text: '{response.text}'")
        raw_cids = response.text.strip()
        if raw_cids:
             recommended_cids = [cid.strip() for cid in raw_cids.split(',') if cid.strip()]
        logger.info(f"Parsed recommended CIDs: {recommended_cids}")
    except Exception as e:
        logger.error(f"Error calling Gemini API or parsing response: {e}", exc_info=True)
        if 'response' in locals() and hasattr(response, 'prompt_feedback'):
             logger.error(f"Gemini Prompt Feedback: {response.prompt_feedback}")
        recommended_cids = []
    return recommended_cids


# --- Main Orchestration Function (expects string user_id) ---
async def generate_club_recommendations(user_id: str, db: Session) -> List[Club]: # Return Club objects
    """
    Generates club recommendations for a given user ID (string).
    Fetches user profile, all clubs, calls Gemini, and returns recommended clubs.
    """
    # 1. Fetch User Profile (using string ID)
    user_profile = get_user_profile(user_id, db)
    if not user_profile:
        # Decide how to handle: return empty list or raise error?
        # Raising error might be better to signal issue upstream.
        # For now, returning empty list as before.
        logger.warning(f"User profile not found for user_id: {user_id}")
        return []

    # 2. Fetch All Clubs
    try:
        all_clubs = db.query(Club).all()
        if not all_clubs:
            logger.warning("No clubs found in the database.")
            return []
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching clubs: {e}", exc_info=True)
        # Consider raising HTTPException here for DB errors
        return []

    # 3. Create Prompt
    prompt = create_recommendation_prompt(user_profile, all_clubs)
    logger.debug(f"Generated Prompt for Gemini:\n{prompt}")

    # 4. Get Recommended CIDs from Gemini
    recommended_cids = await get_recommendations_from_gemini(prompt)
    if not recommended_cids:
        logger.info(f"No recommendations received from Gemini for user {user_id}.")
        return []

    # 5. Fetch Full Club Details for Recommended CIDs
    try:
        recommended_clubs_query = db.query(Club).filter(Club.cid.in_(recommended_cids))
        recommended_clubs_list = recommended_clubs_query.all()

        # Optional: Preserve the order returned by Gemini
        recommended_clubs_dict = {club.cid: club for club in recommended_clubs_list}
        ordered_recommended_clubs = [recommended_clubs_dict[cid] for cid in recommended_cids if cid in recommended_clubs_dict]

    except SQLAlchemyError as e:
        logger.error(f"Database error fetching recommended clubs: {e}", exc_info=True)
        # Consider raising HTTPException here
        return []

    # 6. Return the list of Club objects. FastAPI handles conversion to ClubResponse.
    logger.info(f"Returning {len(ordered_recommended_clubs)} recommendations for user {user_id}.")
    return ordered_recommended_clubs