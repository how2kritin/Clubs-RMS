from os import getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# just import whatever routers you want to import from ./routers here.
from routers import habits_router
from routers import recommendations_router
from utils.database_utils import SessionLocal, init_db, reset_db

# FastAPI instance here, along with CORS middleware
DEBUG = getenv("DEBUG_BACKEND", "False").lower() in ("true", "t", "1")
app = FastAPI(
    debug=DEBUG,
    title="Recruitment Management System backend",
    description="Backend for the RMS-IIITH",
)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["GET", "POST"],
)


# tasks to run on server startup.
@app.on_event("startup")
async def on_startup():
    # initialize the postgresql database.
    reset_db()
    db = SessionLocal()
    db.close()


# base path for checking if the backend is alive.
@app.get("/", tags=["General"])
async def index():
    return {
        "message": "hello, you have reached the backend API service. what would you like to order?"
    }


# mount the imported routers on a path here.
app.include_router(habits_router.router, prefix="/habits")
app.include_router(recommendations_router.router, prefix="/recommendations")
