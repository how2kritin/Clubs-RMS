from os import getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import routers.applications_router as applications_router
import routers.clubs_router as clubs_router
# just import whatever routers you want to import from ./routers here.
import routers.users_router as users_router
from models.clubs.clubs_sync import sync_clubs
from utils.database_utils import init_db, SessionLocal

# FastAPI instance here, along with CORS middleware
DEBUG = getenv("DEBUG_BACKEND", "False").lower() in ("true", "t", "1")
app = FastAPI(debug=DEBUG, title="Recruitment Management System backend", description="Backend for the RMS-IIITH", )
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=["*"], allow_headers=["*"],
                   allow_methods=["GET", "POST"], )

# tasks to run on server startup.
@app.on_event("startup")
async def on_startup():
    # initialize the postgresql database.
    init_db()
    db = SessionLocal()

    # sync clubs data from Clubs Council API
    try:
        await sync_clubs(db)
    finally:
        db.close()


# base path for checking if the backend is alive.
@app.get("/", tags=["General"])
async def index():
    return {"message": "hello, you have reached the backend API service. what would you like to order?"}


# mount the imported routers on a path here.
app.include_router(users_router.router, prefix="/api/user", tags=["User Management"])
app.include_router(clubs_router.router, prefix="/api/club", tags=["Club Management"])
app.include_router(applications_router.router, prefix="/api/application", tags=["Application Management"], )