from fastapi import APIRouter, status
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get("/", status_code=status.HTTP_200_OK)
async def login_cas_redirect():
    return {"hello": "world"}
