import secrets
from datetime import datetime, timedelta
from os import getenv

from fastapi import HTTPException, Cookie, Depends
from pytz import timezone, UTC
from sqlalchemy.orm import Session

from models.users.session_model import Session as SessionModel
from models.users.users_model import User
from utils.crypto_utils import encrypt_data, decrypt_data
from utils.database_utils import get_db

SESSION_COOKIE_NAME = "session_token"
SESSION_EXPIRY_DAYS = int(getenv("SESSION_EXPIRY_DAYS", 5))


# create a new session and return the encrypted session ID
def create_session(user_uid: str, user_agent: str, ip_address: str, db: Session) -> str:
    # unique random session ID
    session_id = secrets.token_urlsafe(32)
    encrypted_id = encrypt_data(session_id)

    # expiry time
    expires_at = datetime.now(timezone("UTC")) + timedelta(days=SESSION_EXPIRY_DAYS)

    session = SessionModel(
        id=session_id,
        user_uid=user_uid,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    db.add(session)
    db.commit()

    return encrypted_id


# common session validation logic.
def validate_session(encrypted_session_id: str, db: Session):
    """
    :return: (user_dict, session_id (decrypted)) if valid, (None, None) if invalid.
    """
    # missing cookie case
    if encrypted_session_id is None:
        return None, None

    session_id = decrypt_data(encrypted_session_id)
    if session_id is None:
        return None, None

    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    # check if session exists and is not expired
    now = datetime.now(timezone("UTC"))
    if session is None or session.expires_at.replace(tzinfo=UTC) < now:
        if session:  # if session exists but is expired, delete it
            db.delete(session)
            db.commit()
        return None, None

    # query the user
    user = db.query(User).filter(User.uid == session.user_uid).first()

    if user is None:
        # delete invalid session
        db.delete(session)
        db.commit()
        return None, None

    # return user data and original encrypted session ID
    user_data = {
        "uid": user.uid,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "roll_number": user.roll_number,
    }

    return user_data, session_id


# get current user's details
async def get_current_user(
    encrypted_session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: Session = Depends(get_db),
):
    user_data, _ = validate_session(encrypted_session_id, db)

    if user_data is None:
        raise HTTPException(status_code=401, detail="Not Authenticated")

    return user_data


# check if the current user is logged in. If yes, return the decrypted session id.
async def check_current_user(
    encrypted_session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: Session = Depends(get_db),
):
    _, session_id = validate_session(encrypted_session_id, db)
    return session_id


# invalidate/delete a session
def invalidate_session(encrypted_session_id: str, db: Session) -> bool:
    if not encrypted_session_id:
        return False

    session_id = decrypt_data(encrypted_session_id)
    if session_id is None:
        return False

    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if session:
        db.delete(session)
        db.commit()
        return True
    return False
