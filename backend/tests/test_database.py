"""Tests for the database session factory and get_db dependency."""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.models.database import Base, get_db


def _make_in_memory_session_factory():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_get_db_yields_a_session_and_closes_it():
    """get_db() must yield exactly one session and close it after the generator exits."""
    # Monkeypatch SessionLocal to use an in-memory engine
    import app.models.database as db_module

    original = db_module.SessionLocal
    db_module.SessionLocal = _make_in_memory_session_factory()
    try:
        gen = get_db()
        session = next(gen)
        # Session should be open and able to execute a simple query
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
        # Exhaust the generator (triggers finally block → session.close())
        try:
            next(gen)
        except StopIteration:
            pass
        # After close the session is no longer in an open transaction
        assert not session.in_transaction()
    finally:
        db_module.SessionLocal = original


def test_init_db_creates_tables():
    """init_db() should create vme_matrix and migration_paths tables."""
    engine = create_engine("sqlite:///:memory:")
    # Temporarily swap engine in the module
    import app.models.database as db_module

    original_engine = db_module.engine
    db_module.engine = engine
    try:
        db_module.init_db()
        # Verify both tables exist by querying the sqlite_master catalog
        with engine.connect() as conn:
            tables = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            ).fetchall()
            table_names = {row[0] for row in tables}
        assert "vme_matrix" in table_names
        assert "migration_paths" in table_names
    finally:
        db_module.engine = original_engine
