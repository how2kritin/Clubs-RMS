"""
Some users functionality copied over from
https://github.com/IMS-IIITH/backend/blob/master/routers/users_router.py,
courtesy of https://github.com/bhavberi
"""
from os import getenv

from cas import CASClient
from fastapi import APIRouter, Depends, Response, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from models.users_config import user_login_cas, user_logout, user_extend_cookie
from utils.auth_utils import check_current_user, get_current_user
from utils.database_utils import get_db
from sqlalchemy.orm import Session

CAS_SERVER_URL = getenv('CAS_SERVER_URL')
CAS_SERVICE_URL = f"{getenv('BASE_URL')}/{getenv('SUBPATH')}/user/login"

cas_client = CASClient(version=3, service_url=CAS_SERVICE_URL, server_url=CAS_SERVER_URL)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# User Login via CAS. Returns the URL for the frontend to redirect to CAS login
@router.post("/login", status_code=status.HTTP_200_OK)
async def login_cas_redirect():
    cas_login_url = cas_client.get_login_url()
    return {'loginUrl': cas_login_url}


# User Login via CAS. Process the ticket received from CAS
@router.get("/login", status_code=status.HTTP_200_OK)
async def login_cas(request: Request, response: Response, db: Session = Depends(get_db)):
    ticket = request.query_params.get('ticket')
    access_token = await user_login_cas(response, ticket, cas_client, db)
    response = RedirectResponse(url=f"{getenv('FRONTEND_URL')}/dashboard", status_code=302)
    response.set_cookie(key="access_token_RMS", value=access_token, httponly=True)
    return response


# User Logout
@router.post("/logout", status_code=status.HTTP_202_ACCEPTED)
async def logout(response: Response, current_user: str | None = Depends(check_current_user)):
    return await user_logout(response, current_user)


@router.post("/extend_cookie", status_code=status.HTTP_200_OK)
async def extend_cookie(request: Request, response: Response, user_data=Depends(get_current_user), ):
    username, email = user_data["username"], user_data["email"]
    return await user_extend_cookie(response, username, email)

@router.get("/validate", status_code=status.HTTP_200_OK)
async def validate_user(request: Request, response: Response, current_user=Depends(check_current_user)):
    if current_user is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"valid": 0}
    return {"valid": 1}