"""Database infrastructure for the AcmeCloud checkout service.

This module owns the SQLAlchemy engine and session factory.

The checkout service connects to the AcmeCloud PostgreSQL database
through the DATABASE_URL environment variable. Database sessions are
created per request and always closed after use.
"""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    """Return the process-wide SQLAlchemy session factory."""
    engine = create_engine(
        get_settings().database_url,
        pool_pre_ping=True,
    )

    return sessionmaker(
        bind=engine,
        class_=Session,
        autoflush=False,
        autocommit=False,
    )


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for the lifetime of a request."""
    db = get_session_factory()()

    try:
        yield db
    finally:
        db.close()
