"""Tests for /api/admin/matrix and /api/admin/migration-paths endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.database import Base, get_db
from app.models.seed import seed_database

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    """TestClient with a fresh in-memory seeded DB injected via dependency override."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    seed_database(db)

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)
    db.close()
    Base.metadata.drop_all(engine)


# ---------------------------------------------------------------------------
# GET /api/admin/matrix
# ---------------------------------------------------------------------------


def test_get_matrix_returns_seeded_entries(client: TestClient) -> None:
    resp = client.get("/api/admin/matrix")
    assert resp.status_code == 200
    entries = resp.json()
    assert isinstance(entries, list)
    assert len(entries) > 0
    first = entries[0]
    for field in ("id", "os_vendor", "os_family", "os_versions", "classification_tier"):
        assert field in first


# ---------------------------------------------------------------------------
# POST /api/admin/matrix
# ---------------------------------------------------------------------------


def test_post_matrix_creates_entry(client: TestClient) -> None:
    payload = {
        "os_vendor": "TestVendor",
        "os_family": "TestOS",
        "os_versions": "1.0, 2.0",
        "classification_tier": "officially_supported",
        "notes": "Test entry",
    }
    resp = client.post("/api/admin/matrix", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["os_family"] == "TestOS"
    assert body["os_vendor"] == "TestVendor"


def test_post_matrix_entry_appears_in_get(client: TestClient) -> None:
    payload = {
        "os_vendor": "AnotherVendor",
        "os_family": "AnotherOS",
        "os_versions": "3.0",
        "classification_tier": "needs_info",
    }
    create_resp = client.post("/api/admin/matrix", json=payload)
    new_id = create_resp.json()["id"]

    get_resp = client.get("/api/admin/matrix")
    ids = [e["id"] for e in get_resp.json()]
    assert new_id in ids


# ---------------------------------------------------------------------------
# PUT /api/admin/matrix/{id}
# ---------------------------------------------------------------------------


def test_put_matrix_updates_entry(client: TestClient) -> None:
    create_resp = client.post(
        "/api/admin/matrix",
        json={
            "os_vendor": "V1",
            "os_family": "UpdateMe",
            "os_versions": "1",
            "classification_tier": "needs_info",
        },
    )
    entry_id = create_resp.json()["id"]

    update_resp = client.put(
        f"/api/admin/matrix/{entry_id}",
        json={"os_versions": "1, 2, 3"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["os_versions"] == "1, 2, 3"


def test_put_matrix_returns_404_for_missing_id(client: TestClient) -> None:
    resp = client.put("/api/admin/matrix/999999", json={"os_versions": "x"})
    assert resp.status_code == 404
    assert resp.json()["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# DELETE /api/admin/matrix/{id}
# ---------------------------------------------------------------------------


def test_delete_matrix_removes_entry(client: TestClient) -> None:
    create_resp = client.post(
        "/api/admin/matrix",
        json={
            "os_vendor": "TempVendor",
            "os_family": "TempOS",
            "os_versions": "0",
            "classification_tier": "not_supported",
        },
    )
    entry_id = create_resp.json()["id"]

    del_resp = client.delete(f"/api/admin/matrix/{entry_id}")
    assert del_resp.status_code == 204

    get_resp = client.get("/api/admin/matrix")
    ids = [e["id"] for e in get_resp.json()]
    assert entry_id not in ids


def test_delete_matrix_returns_404_for_missing_id(client: TestClient) -> None:
    resp = client.delete("/api/admin/matrix/999999")
    assert resp.status_code == 404
    assert resp.json()["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# GET /api/admin/migration-paths
# ---------------------------------------------------------------------------


def test_get_migration_paths_returns_seeded_data(client: TestClient) -> None:
    resp = client.get("/api/admin/migration-paths")
    assert resp.status_code == 200
    paths = resp.json()
    assert isinstance(paths, list)
    assert len(paths) > 0
    first = paths[0]
    for field in ("id", "classification_tier", "guidance_text"):
        assert field in first


# ---------------------------------------------------------------------------
# PUT /api/admin/migration-paths/{id}
# ---------------------------------------------------------------------------


def test_put_migration_path_updates_guidance_text(client: TestClient) -> None:
    paths = client.get("/api/admin/migration-paths").json()
    path_id = paths[0]["id"]

    new_text = "Updated guidance text for testing."
    resp = client.put(
        f"/api/admin/migration-paths/{path_id}",
        json={"guidance_text": new_text},
    )
    assert resp.status_code == 200
    assert resp.json()["guidance_text"] == new_text


def test_put_migration_path_returns_404_for_missing_id(client: TestClient) -> None:
    resp = client.put(
        "/api/admin/migration-paths/999999",
        json={"guidance_text": "irrelevant"},
    )
    assert resp.status_code == 404
    assert resp.json()["code"] == "NOT_FOUND"
