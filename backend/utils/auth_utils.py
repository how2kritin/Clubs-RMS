"""
Auth utils copied over from https://github.com/IMS-IIITH/backend/blob/master/utils/auth_utils.py,
courtesy of https://github.com/bhavberi
"""

from datetime import datetime, timedelta
from os import getenv
from typing import Optional

from fastapi import HTTPException, Cookie, Depends
from jose import JWTError, jwt
from pytz import timezone

from sqlalchemy.orm import Session
from utils.database_utils import get_db
from models.users.users_model import User

# JWT Authentication
SECRET_KEY = (getenv("JWT_SECRET_KEY", "this_is_my_very_secretive_secret") + "__RMS__")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = int(getenv("ACCESS_TOKEN_EXPIRE_DAYS", 5))


# Create Access Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone("UTC")) + expires_delta
    else:
        expire = datetime.now(timezone("UTC")) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Get current user info based on JWT token stored in cookie
async def get_current_user(access_token_RMS: str = Cookie(None), db: Session = Depends(get_db)):
    if access_token_RMS is None:
        raise HTTPException(status_code=401, detail="Not Authenticated")

    try:
        payload = jwt.decode(access_token_RMS, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("uid")

        if uid is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        # query the user from the local database
        user = db.query(User).filter(User.uid == uid).first()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found in database")

        return {
            "uid": user.uid,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roll_number": user.roll_number
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


# Function to check if the current user is logged in, based on the JWT token stored in the cookie
async def check_current_user(access_token_RMS: str = Cookie(None), db: Session = Depends(get_db)):
    if access_token_RMS is None:
        return None

    try:
        payload = jwt.decode(access_token_RMS, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("uid")

        if uid is None:
            return None

        # query the user from the local database
        user = db.query(User).filter(User.uid == uid).first()

        if user is None:
            return None

        return access_token_RMS

    except JWTError:
        return None
