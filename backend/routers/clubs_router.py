from fastapi import APIRouter, status
from starlette.responses import Response

router = APIRouter()


@router.get("/all_club_info", status_code=status.HTTP_200_OK)
async def get_all_club_information(response: Response):
    pass
