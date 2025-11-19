""" Main file for the application. """

from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.configs import app_config
from app.database import init_db
from app.routers import file_router, file_upload_router
from app.logger import get_logger
from app.database import sync_database


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Lifespan context manager for startup and shutdown events. """
    try:
        # Startup: Initialize database
        print("Initializing database...")
        init_db()
        sync_database()
        yield
    except SQLAlchemyError as e:
        logger.exception("Error creating database tables: %s", str(e))
        logger.warning(
            "Application will continue, but database operations may fail")

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["App"])
def read_root():
    """ Read the root endpoint. """

    return {"message": "Hello, World!"}


app.include_router(file_router)
app.include_router(file_upload_router)
