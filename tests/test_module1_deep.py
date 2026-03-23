"""Module 1 - Deep Testing for Tenant, Customer, Environment CRUD.
Validated robustness, correctness, edge cases, and schema integrity.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid
from datetime import datetime

from backend.app.main import app
from backend.app.database import Base, get_db

# Setup in-memory SQLite for deep tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
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

# --- PHASE 2: FUNCTIONAL FLOW TESTS ---

def test_full_lifecycle_flow(client):
    # 1. Create Tenant
    t_resp = client.post("/api/v1/tenants/", json={
        "name": "Deep Test Tenant",
        "slug": "deep-test",
        "plan": "professional"
    })
    assert t_resp.status_code == 201
    tenant = t_resp.json()
    tenant_id = tenant["id"]
    assert uuid.UUID(tenant_id)
    
    # 2. Create Multiple Customers
    c1 = client.post("/api/v1/customers/", json={
        "name": "Customer 1",
        "tenant_id": tenant_id,
        "industry": "Tech"
    })
    c2 = client.post("/api/v1/customers/", json={
        "name": "Customer 2",
        "tenant_id": tenant_id
    })
    assert c1.status_code == 201
    assert c2.status_code == 201
    
    # 3. Create Multiple Environments
    cust1_id = c1.json()["id"]
    e1 = client.post("/api/v1/environments/", json={
        "name": "Prod",
        "customer_id": cust1_id,
        "env_type": "production"
    })
    e2 = client.post("/api/v1/environments/", json={
        "name": "Staging",
        "customer_id": cust1_id,
        "env_type": "staging"
    })
    assert e1.status_code == 201
    assert e2.status_code == 201

    # 4. Retrieval & Count
    list_tenants = client.get("/api/v1/tenants/")
    assert len(list_tenants.json()) == 1
    
    list_customers = client.get(f"/api/v1/customers/?tenant_id={tenant_id}")
    assert len(list_customers.json()) == 2

# --- PHASE 3: MULTI-TENANT ISOLATION ---

def test_tenant_isolation(client):
    t1 = client.post("/api/v1/tenants/", json={"name": "Tenant A", "slug": "t-a"}).json()
    t2 = client.post("/api/v1/tenants/", json={"name": "Tenant B", "slug": "t-b"}).json()
    
    client.post("/api/v1/customers/", json={"name": "C-A", "tenant_id": t1["id"]})
    client.post("/api/v1/customers/", json={"name": "C-B", "tenant_id": t2["id"]})
    
    resp_a = client.get(f"/api/v1/customers/?tenant_id={t1['id']}")
    assert len(resp_a.json()) == 1
    assert resp_a.json()[0]["name"] == "C-A"

# --- PHASE 4: EDGE CASES ---

def test_create_duplicate_tenant_slug(client):
    payload = {"name": "Unique", "slug": "unique-slug"}
    client.post("/api/v1/tenants/", json=payload)
    resp = client.post("/api/v1/tenants/", json=payload)
    assert resp.status_code == 409

def test_create_customer_invalid_tenant(client):
    resp = client.post("/api/v1/customers/", json={
        "name": "Ghost",
        "tenant_id": str(uuid.uuid4())
    })
    assert resp.status_code == 404

# --- PHASE 5: SCHEMA VALIDATION ---

def test_schema_leakage_check(client):
    t_resp = client.post("/api/v1/tenants/", json={"name": "Schema Check", "slug": "schema-check"})
    data = t_resp.json()
    expected_keys = {"id", "name", "slug", "plan", "is_active", "created_at", "updated_at"}
    assert set(data.keys()) == expected_keys

# --- PHASE 8: STARTUP & HEALTH ---

def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
