"""Database infrastructure for the AcmeCloud checkout service.

This module owns the SQLAlchemy engine and session factory.

The checkout service connects to the AcmeCloud PostgreSQL database
through the DATABASE_URL environment variable. Database sessions are
created per request and always closed after use.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for the lifetime of a request.

    The session is closed even when the request raises an exception.
    Transaction commits remain explicit in the calling code.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
