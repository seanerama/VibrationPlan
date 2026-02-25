"""Tests for seed_database() — population and idempotency."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.constants import ALL_TIERS
from app.models.database import Base
from app.models.migration_paths import MigrationPath
from app.models.seed import _MIGRATION_PATHS_SEED, _VME_MATRIX_SEED, seed_database
from app.models.vme_matrix import VmeMatrix


@pytest.fixture
def db_session():
    """Fresh in-memory database session for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_seed_populates_vme_matrix(db_session):
    seed_database(db_session)
    count = db_session.query(VmeMatrix).count()
    assert count == len(_VME_MATRIX_SEED)
    assert count > 0


def test_seed_populates_migration_paths(db_session):
    seed_database(db_session)
    count = db_session.query(MigrationPath).count()
    assert count == len(_MIGRATION_PATHS_SEED)
    assert count > 0


def test_seed_is_idempotent_for_vme_matrix(db_session):
    """Calling seed_database twice must not duplicate rows."""
    seed_database(db_session)
    seed_database(db_session)
    count = db_session.query(VmeMatrix).count()
    assert count == len(_VME_MATRIX_SEED)


def test_seed_is_idempotent_for_migration_paths(db_session):
    seed_database(db_session)
    seed_database(db_session)
    count = db_session.query(MigrationPath).count()
    assert count == len(_MIGRATION_PATHS_SEED)


def test_seed_migration_paths_cover_all_tiers(db_session):
    """Every classification tier must have at least one migration path."""
    seed_database(db_session)
    seeded_tiers = {
        row.classification_tier for row in db_session.query(MigrationPath).all()
    }
    for tier in ALL_TIERS:
        assert tier in seeded_tiers, f"No migration path seeded for tier: {tier}"


def test_seed_vme_matrix_all_tiers_represented(db_session):
    """Every classification tier must appear at least once in the matrix seed."""
    seed_database(db_session)
    seeded_tiers = {row.classification_tier for row in db_session.query(VmeMatrix).all()}
    for tier in ALL_TIERS:
        assert tier in seeded_tiers, f"No vme_matrix entry seeded for tier: {tier}"


def test_seed_migration_paths_tier_defaults_have_null_os_family(db_session):
    """Tier-level default migration paths must have os_family = NULL."""
    seed_database(db_session)
    rows = db_session.query(MigrationPath).all()
    for row in rows:
        # All seeded rows use NULL os_family (tier-level defaults only)
        assert row.os_family is None, (
            f"Expected NULL os_family for tier {row.classification_tier}, "
            f"got {row.os_family!r}"
        )
