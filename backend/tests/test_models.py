"""Tests for VmeMatrix and MigrationPath ORM models (CRUD)."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.constants import TIER_OFFICIALLY_SUPPORTED, TIER_NOT_SUPPORTED
from app.models.database import Base
from app.models.migration_paths import MigrationPath
from app.models.vme_matrix import VmeMatrix


@pytest.fixture
def db_session():
    """In-memory SQLite session with fresh tables for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


# ---------------------------------------------------------------------------
# VmeMatrix tests
# ---------------------------------------------------------------------------


def test_vme_matrix_create_and_read(db_session):
    row = VmeMatrix(
        os_vendor="Microsoft",
        os_family="Windows Server",
        os_versions="2019,2022",
        classification_tier=TIER_OFFICIALLY_SUPPORTED,
        notes="HPE validated",
    )
    db_session.add(row)
    db_session.commit()

    fetched = db_session.query(VmeMatrix).first()
    assert fetched is not None
    assert fetched.os_vendor == "Microsoft"
    assert fetched.os_family == "Windows Server"
    assert fetched.os_versions == "2019,2022"
    assert fetched.classification_tier == TIER_OFFICIALLY_SUPPORTED
    assert fetched.notes == "HPE validated"
    assert fetched.id is not None


def test_vme_matrix_update(db_session):
    row = VmeMatrix(
        os_vendor="Canonical",
        os_family="Ubuntu",
        os_versions="20.04",
        classification_tier=TIER_OFFICIALLY_SUPPORTED,
    )
    db_session.add(row)
    db_session.commit()

    row.os_versions = "20.04,22.04"
    db_session.commit()

    fetched = db_session.query(VmeMatrix).filter_by(os_family="Ubuntu").first()
    assert fetched.os_versions == "20.04,22.04"


def test_vme_matrix_delete(db_session):
    row = VmeMatrix(
        os_vendor="IBM",
        os_family="OS/2",
        os_versions="any",
        classification_tier=TIER_NOT_SUPPORTED,
    )
    db_session.add(row)
    db_session.commit()

    db_session.delete(row)
    db_session.commit()

    assert db_session.query(VmeMatrix).count() == 0


def test_vme_matrix_notes_nullable(db_session):
    """notes column should accept NULL."""
    row = VmeMatrix(
        os_vendor="Generic",
        os_family="Unknown",
        os_versions="any",
        classification_tier="needs_info",
        notes=None,
    )
    db_session.add(row)
    db_session.commit()

    fetched = db_session.query(VmeMatrix).first()
    assert fetched.notes is None


def test_vme_matrix_repr(db_session):
    row = VmeMatrix(
        os_vendor="Red Hat",
        os_family="RHEL",
        os_versions="8,9",
        classification_tier=TIER_OFFICIALLY_SUPPORTED,
    )
    db_session.add(row)
    db_session.commit()
    r = repr(row)
    assert "VmeMatrix" in r
    assert "Red Hat" in r
    assert "RHEL" in r


# ---------------------------------------------------------------------------
# MigrationPath tests
# ---------------------------------------------------------------------------


def test_migration_path_create_and_read(db_session):
    row = MigrationPath(
        classification_tier=TIER_OFFICIALLY_SUPPORTED,
        os_family=None,
        guidance_text="Proceed with standard P2V migration tooling.",
    )
    db_session.add(row)
    db_session.commit()

    fetched = db_session.query(MigrationPath).first()
    assert fetched is not None
    assert fetched.classification_tier == TIER_OFFICIALLY_SUPPORTED
    assert fetched.os_family is None
    assert "P2V" in fetched.guidance_text


def test_migration_path_update(db_session):
    row = MigrationPath(
        classification_tier=TIER_NOT_SUPPORTED,
        guidance_text="Old text.",
    )
    db_session.add(row)
    db_session.commit()

    row.guidance_text = "Updated text."
    db_session.commit()

    fetched = db_session.query(MigrationPath).first()
    assert fetched.guidance_text == "Updated text."


def test_migration_path_delete(db_session):
    row = MigrationPath(
        classification_tier="needs_review",
        guidance_text="Review with customer.",
    )
    db_session.add(row)
    db_session.commit()

    db_session.delete(row)
    db_session.commit()

    assert db_session.query(MigrationPath).count() == 0


def test_migration_path_os_family_nullable(db_session):
    """os_family is NULL for tier-level defaults."""
    row = MigrationPath(
        classification_tier="needs_info",
        os_family=None,
        guidance_text="Gather more info.",
    )
    db_session.add(row)
    db_session.commit()

    fetched = db_session.query(MigrationPath).first()
    assert fetched.os_family is None


def test_migration_path_repr(db_session):
    row = MigrationPath(
        classification_tier="supported_vdi",
        os_family="Citrix Virtual Apps",
        guidance_text="VDI guidance.",
    )
    db_session.add(row)
    db_session.commit()
    r = repr(row)
    assert "MigrationPath" in r
    assert "supported_vdi" in r
    assert "Citrix Virtual Apps" in r
