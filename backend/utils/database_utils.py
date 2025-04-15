import logging
from os import getenv

from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/rms_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logger = logging.getLogger(__name__)


def init_db():
    Base.metadata.create_all(bind=engine)


# dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def delete_db():
    Base.metadata.drop_all(bind=engine)

# util to drop all tables (do not recreate them). returns true if successful, false if it fails.
def drop_all_tables() -> bool:
    try:
        # Get inspector to check existing tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # Log the tables that will be dropped
        logger.warning(f"Dropping {len(tables)} tables: {', '.join(tables)}")

        # Drop all tables defined in the metadata
        Base.metadata.drop_all(bind=engine)

        logger.info("All tables dropped successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to drop tables: {str(e)}")
        return False


# reset the database by dropping all tables and recreating them.
def reset_db():
    try:
        # Drop all tables
        success = drop_all_tables()
        if not success:
            return False

        # Recreate all tables
        init_db()

        logger.info("Database reset successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to reset database: {str(e)}")
        return False


if __name__ == "__main__":
    init_db()
