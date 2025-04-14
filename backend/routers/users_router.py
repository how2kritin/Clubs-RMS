"""
Some users functionality copied over from
https://github.com/IMS-IIITH/backend/blob/master/routers/users_router.py,
courtesy of https://github.com/bhavberi
"""
from os import getenv

from cas import CASClient
from fastapi import APIRouter, Depends, Response, Request, status
from models.users.users_config import user_login_cas, user_info
from utils.database_utils import get_db
from sqlalchemy.orm import Session

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
    return await user_login_cas(response, ticket, cas_client, db)


# Fetch the info of the currently logged-in user
@router.get("/user_info", status_code=status.HTTP_200_OK)
async def get_user_info(request: Request, response: Response):
    return await user_info(response)
