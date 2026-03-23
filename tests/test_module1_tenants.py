"""Module 1 Task 1 - Tests for Tenant, Customer, Environment API.

Runs against in-memory SQLite for isolation.
Run with: pytest tests/test_module1_tenants.py -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Use in-memory SQLite for tests
SQLITE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Health Check ───────────────────────────────────────────────────────────────

def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "socai-platform"


# ── Tenant Tests ──────────────────────────────────────────────────────────────

def test_create_tenant(client):
    resp = client.post("/api/v1/tenants/", json={
        "name": "ACME Corp",
        "slug": "acme-corp",
        "plan": "starter"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "acme-corp"
    assert data["is_active"] is True
    assert "id" in data


def test_create_tenant_duplicate_slug(client):
    payload = {"name": "Test", "slug": "test-slug", "plan": "starter"}
    client.post("/api/v1/tenants/", json=payload)
    resp = client.post("/api/v1/tenants/", json=payload)
    assert resp.status_code == 409


def test_list_tenants(client):
    client.post("/api/v1/tenants/", json={"name": "T1", "slug": "t1", "plan": "starter"})
    client.post("/api/v1/tenants/", json={"name": "T2", "slug": "t2", "plan": "professional"})
    resp = client.get("/api/v1/tenants/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_tenant_not_found(client):
    resp = client.get("/api/v1/tenants/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_update_tenant(client):
    create_resp = client.post("/api/v1/tenants/", json={"name": "OldName", "slug": "old-slug", "plan": "starter"})
    tenant_id = create_resp.json()["id"]
    resp = client.patch(f"/api/v1/tenants/{tenant_id}", json={"name": "NewName", "plan": "enterprise"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "NewName"


def test_delete_tenant(client):
    create_resp = client.post("/api/v1/tenants/", json={"name": "ToDelete", "slug": "to-delete", "plan": "starter"})
    tenant_id = create_resp.json()["id"]
    resp = client.delete(f"/api/v1/tenants/{tenant_id}")
    assert resp.status_code == 204
    get_resp = client.get(f"/api/v1/tenants/{tenant_id}")
    assert get_resp.status_code == 404


# ── Customer Tests ────────────────────────────────────────────────────────────

def test_create_customer(client):
    tenant = client.post("/api/v1/tenants/", json={"name": "MSP", "slug": "msp", "plan": "professional"}).json()
    resp = client.post("/api/v1/customers/", json={
        "name": "Customer A",
        "domain": "customera.com",
        "contact_email": "admin@customera.com",
        "tenant_id": tenant["id"]
    })
    assert resp.status_code == 201
    assert resp.json()["name"] == "Customer A"


def test_create_customer_invalid_tenant(client):
    resp = client.post("/api/v1/customers/", json={
        "name": "Orphan",
        "tenant_id": "00000000-0000-0000-0000-000000000000"
    })
    assert resp.status_code == 404
