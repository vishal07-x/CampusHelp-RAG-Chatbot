import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings
from app.core.logging import logger

database_url = settings.DATABASE_URL

# Automatically handle SQLite connect_args
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        database_url,
        connect_args=connect_args,
        echo=False,
        future=True
    )
except Exception as e:
    logger.warning(f"Failed to connect to primary DB ({database_url}): {e}. Falling back to SQLite.")
    sqlite_url = f"sqlite:///{settings.BASE_DIR / 'campushelp.db'}"
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
        echo=False,
        future=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
