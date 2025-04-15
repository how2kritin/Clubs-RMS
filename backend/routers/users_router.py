"""
Some users functionality copied over from
https://github.com/IMS-IIITH/backend/blob/master/routers/users_router.py,
courtesy of https://github.com/bhavberi
"""
from os import getenv

from cas import CASClient
from fastapi import APIRouter, Depends, Response, Request, status, Cookie
from sqlalchemy.orm import Session

from models.users.users_config import user_login_cas, user_logout
from utils.database_utils import get_db
from utils.session_utils import SESSION_COOKIE_NAME, check_current_user, get_current_user
from fastapi.responses import RedirectResponse


CAS_SERVER_URL = getenv('CAS_SERVER_URL')
CAS_SERVICE_URL = f"{getenv('BASE_URL')}/{getenv('SUBPATH')}/user/login"

cas_client = CASClient(version=3, service_url=CAS_SERVICE_URL, server_url=CAS_SERVER_URL)

router = APIRouter()


# User Login via CAS. Returns the URL for the frontend to redirect to CAS login
@router.post("/login", status_code=status.HTTP_200_OK)
async def login_cas_redirect():
    cas_login_url = cas_client.get_login_url()
    return {'loginUrl': cas_login_url}


# User Login via CAS. Process the ticket received from CAS
@router.get("/login", status_code=status.HTTP_200_OK)
async def login_cas(request: Request, response: Response, db: Session = Depends(get_db)):
    ticket = request.query_params.get('ticket')
    user_agent = request.headers.get("user-agent", "")
    ip_address = request.client.host if request.client else None
    encrypted_session_id = await user_login_cas(response, ticket, user_agent, ip_address, cas_client, db)
    response = RedirectResponse(url=f"{getenv('FRONTEND_URL')}/profile")
    response.set_cookie(key=SESSION_COOKIE_NAME, value=encrypted_session_id, httponly=True, secure=True,
        samesite="lax"  # protection against CSRF
    )
    return response


# Fetch the info of the currently logged-in user
@router.get("/user_info", status_code=status.HTTP_200_OK)
async def get_user_info(current_user: dict = Depends(get_current_user)):
    print(current_user)
    return current_user


# Check if a user is logged in
@router.get("/is_authenticated", status_code=status.HTTP_200_OK)
async def check_login(session: str = Depends(check_current_user)):
    return {"authenticated": session is not None}


# User Logout
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, db: Session = Depends(get_db),
        session_id: str = Cookie(None, alias=SESSION_COOKIE_NAME)):
    return await user_logout(response, session_id, db)
