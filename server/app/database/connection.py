""" Database connection setup. """

from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from fastapi import Depends

from app.configs import app_config
from app.logger import get_logger


logger = get_logger(__name__)


encoded_password = quote_plus(app_config.DB_PASSWORD)
SQLALCHEMY_DATABASE_URL = f"postgresql://{app_config.DB_USER}:{encoded_password}@{app_config.DB_HOST}:{app_config.DB_PORT}/{app_config.DB_NAME}"


# Create database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=app_config.DEBUG
)

# Create Base - this will be imported by models
Base = declarative_base()
# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """ Initialize database by creating all tables. """
    # Import models to ensure they're registered with Base.metadata
    from app.models import FileModel  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """ Dependency for getting database session. """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sync_database():
    """Synchronize database schema with models (drops and recreates all tables).

    WARNING: This will delete all existing data!
    Similar to NestJS synchronize: true behavior.
    Use only in development environment.
    """
    # Import models to ensure they're registered with Base.metadata
    from app.models import FileModel  # noqa: F401

    try:
        # Drop all tables
        logger.warning("Dropping all existing tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped successfully")

        # Create all tables
        logger.info("Creating tables from models...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database synchronized successfully - all tables recreated")
    except Exception as e:
        logger.exception("Error synchronizing database: %s", str(e))
        raise


# Type hint for dependency injection
GetDb = Depends(get_db)
