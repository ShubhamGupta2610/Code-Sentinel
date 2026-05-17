"""Database setup using SQLAlchemy 2.0 with pool_pre_ping for resilience."""
from __future__ import annotations

from typing import Generator

import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from app.core.config import settings

# Wait/retry for DB readiness (helps during container startup)
MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds
ENGINE = None
for attempt in range(1, MAX_RETRIES + 1):
    try:
        ENGINE = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
        with ENGINE.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        break
    except OperationalError:
        if attempt == MAX_RETRIES:
            raise
        time.sleep(RETRY_DELAY)

SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False, future=True, class_=Session)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
