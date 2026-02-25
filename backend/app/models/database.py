"""SQLAlchemy engine, session factory, declarative base, and FastAPI dependency."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    # SQLite-specific: allow connections from multiple threads (needed for tests)
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables defined in the ORM models.

    Safe to call on every startup — SQLAlchemy skips tables that already exist.
    """
    # Import models here so Base.metadata is populated before create_all runs.
    import app.models.migration_paths  # noqa: F401
    import app.models.vme_matrix  # noqa: F401

    Base.metadata.create_all(bind=engine)
