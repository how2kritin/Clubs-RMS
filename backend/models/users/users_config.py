"""
Some users functionality copied over from
https://github.com/IMS-IIITH/backend/blob/master/routers/users_router.py,
courtesy of https://github.com/bhavberi
"""
from cas import CASClientV3
from fastapi import Response
from sqlalchemy.orm import Session

from models.users.users_model import User
from utils.session_utils import create_session, SESSION_COOKIE_NAME, invalidate_session


async def user_login_cas(response: Response, ticket: str, user_agent: str, ip_address: str, cas_client: CASClientV3,
                         db: Session):
    if ticket:
        user, attributes, _ = cas_client.verify_ticket(ticket)
        if user:
            roll = attributes['RollNo']
            email = attributes['E-Mail']
            first_name = attributes['FirstName']
            last_name = attributes['LastName']
            uid = attributes['uid']

            # look up user in database
            db_user = db.query(User).filter(User.uid == uid).first()

            # create if user doesn't exist
            if not db_user:
                db_user = User(uid=uid, email=email, first_name=first_name, last_name=last_name, roll_number=roll)
                db.add(db_user)
                db.commit()
                db.refresh(db_user)

            # create session token and set cookie
            encrypted_session_id = create_session(user_uid=uid, user_agent=user_agent, ip_address=ip_address, db=db)
            # response.set_cookie(key=SESSION_COOKIE_NAME, value=encrypted_session_id, httponly=True, secure=True,
            #     samesite="lax"  # protection against CSRF
            # )
            
    return encrypted_session_id


# log user out by invalidating their session
async def user_logout(response: Response, encrypted_session_id: str, db: Session):
    invalidate_session(encrypted_session_id, db)
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    return {"message": "Logged out successfully"}
