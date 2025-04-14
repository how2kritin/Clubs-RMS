"""
Some users functionality copied over from
https://github.com/IMS-IIITH/backend/blob/master/routers/users_router.py,
courtesy of https://github.com/bhavberi
"""
from cas import CASClientV3
from fastapi import HTTPException, Response

from sqlalchemy.orm import Session
from models.user_model import User
from utils.auth_utils import create_access_token
from utils.ldap_utils import authenticate_user

async def user_login_cas(response: Response, ticket: str, cas_client: CASClientV3, db: Session):
    access_token = None
    if ticket:
        user, attributes, pgtiou = cas_client.verify_ticket(ticket)
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
                db_user = User(
                    uid=uid,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    roll_number=roll
                )
                db.add(db_user)
                db.commit()
                db.refresh(db_user)

            # create access token and set cookie
            access_token = create_access_token(data={
                "username": f"{first_name} {last_name}",
                "email": email
            })
            # response.set_cookie(key="access_token_RMS", value=access_token, httponly=True)

    return access_token


async def user_logout(response: Response, current_user):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not Logged In!")
    response.delete_cookie("access_token_RMS")
    return {"message": "Logged Out Successfully"}


async def user_extend_cookie(response, username, email):
    # Extend the access token/expiry time
    new_access_token = create_access_token(data={"username": username, "email": email})
    response.set_cookie(key="access_token_RMS", value=new_access_token)
    return {"message": "Cookie Extended Successfully"}
