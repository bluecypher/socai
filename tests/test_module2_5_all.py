
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid
from datetime import datetime
from backend.app.main import app
from backend.app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
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

# ==== MODULE 2: Asset & Log Source Tests ====
def test_create_asset(client):
    t = client.post("/api/v1/tenants/", json={"name": "T1", "slug": "t1"}).json()
    c = client.post("/api/v1/customers/", json={"name": "C1", "tenant_id": t["id"]}).json()
    asset = client.post("/api/v1/assets/", json={
        "name": "WebServer01",
        "customer_id": c["id"],
        "ip_address": "192.168.1.10",
        "hostname": "web01.local",
        "asset_type": "server",
        "criticality": "high"
    })
    assert asset.status_code == 201
    data = asset.json()
    assert data["name"] == "WebServer01"
    assert data["criticality"] == "high"
    assert data["is_active"] is True

def test_list_assets_by_customer(client):
    t = client.post("/api/v1/tenants/", json={"name": "T2", "slug": "t2"}).json()
    c1 = client.post("/api/v1/customers/", json={"name": "C1", "tenant_id": t["id"]}).json()
    c2 = client.post("/api/v1/customers/", json={"name": "C2", "tenant_id": t["id"]}).json()
    client.post("/api/v1/assets/", json={"name": "A1", "customer_id": c1["id"]})
    client.post("/api/v1/assets/", json={"name": "A2", "customer_id": c2["id"]})
    resp = client.get(f"/api/v1/assets/?customer_id={c1['id']}")
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "A1"

# ==== MODULE 3: Wazuh Alert Ingestion Tests ====
def test_alert_ingest_raw(client):
    t = client.post("/api/v1/tenants/", json={"name": "T3", "slug": "t3"}).json()
    c = client.post("/api/v1/customers/", json={"name": "C3", "tenant_id": t["id"]}).json()
    resp = client.post("/api/v1/alerts/ingest", json={
        "customer_id": c["id"],
        "source": "wazuh",
        "agent_id": "001",
        "agent_name": "server01",
        "rule_id": "5500",
        "rule_description": "SSH authentication success",
        "rule_level": 3
    })
    assert resp.status_code == 201
    alert = resp.json()
    assert alert["agent_id"] == "001"
    assert alert["status"] == "new"

# ==== MODULE 4: Alert Normalization Tests ====
def test_alert_normalization_wazuh(client):
    t = client.post("/api/v1/tenants/", json={"name": "T4", "slug": "t4"}).json()
    c = client.post("/api/v1/customers/", json={"name": "C4", "tenant_id": t["id"]}).json()
    wazuh_alert = {
        "id": "1234567890",
        "agent": {"id": "002", "name": "dbserver", "ip": "10.0.0.5"},
        "rule": {"id": "5710", "description": "Multiple authentication failures", "level": 10, "groups": ["authentication_failures"]},
        "timestamp": "2026-03-26T12:00:00Z"
    }
    resp = client.post("/api/v1/alerts/ingest", json={
        "customer_id": c["id"],
        "source": "wazuh",
        "raw_data": wazuh_alert
    })
    assert resp.status_code == 201
    alert = resp.json()
    assert alert["normalized"] is True
    assert alert["severity"] == "medium"
    assert alert["rule_level"] == 10
    assert alert["agent_name"] == "dbserver"

def test_alert_severity_mapping(client):
    t = client.post("/api/v1/tenants/", json={"name": "T5", "slug": "t5"}).json()
    c = client.post("/api/v1/customers/", json={"name": "C5", "tenant_id": t["id"]}).json()
    for level, expected_sev in [(2, "informational"), (5, "low"), (10, "medium"), (14, "high"), (18, "critical")]:
        resp = client.post("/api/v1/alerts/ingest", json={
            "customer_id": c["id"],
            "source": "wazuh",
            "raw_data": {"rule": {"level": level}, "agent": {}}
        })
        assert resp.json()["severity"] == expected_sev

# ==== MODULE 5: Case Creation Tests ====
def test_create_case_manually(client):
    t = client.post("/api/v1/tenants/", json={"name": "T6", "slug": "t6"}).json()
    c = client.post("/api/v1/customers/", json={"name": "C6", "tenant_id": t["id"]}).json()
    case = client.post("/api/v1/cases/", json={
        "title": "Suspected malware infection",
        "customer_id": c["id"],
        "description": "Multiple high-severity alerts from host X",
        "severity": "high",
        "priority": "high",
        "tags": ["malware", "urgent"]
    })
    assert case.status_code == 201
    data = case.json()
    assert data["title"] == "Suspected malware infection"
    assert data["status"] == "open"
    assert data["alert_count"] == 0

def test_auto_case_creation_high_severity(client):
    t = client.post("/api/v1/tenants/", json={"name": "T7", "slug": "t7"}).json()
    c = client.post("/api/v1/customers/", json={"name": "C7", "tenant_id": t["id"]}).json()
    for i, sev in enumerate(["high", "critical", "low", "high"]):
        client.post("/api/v1/alerts/ingest", json={
            "customer_id": c["id"],
            "source": "wazuh",
            "agent_id": f"agent{i}",
            "rule_description": f"Alert {i}",
            "rule_level": 15 if sev == "high" else 20 if sev == "critical" else 5,
            "raw_data": {"rule": {"level": 15 if sev == "high" else 20 if sev == "critical" else 5}, "agent": {}}
        })
    auto_resp = client.post(f"/api/v1/cases/auto-create/{c['id']}")
    assert auto_resp.status_code == 200
    result = auto_resp.json()
    assert result["created"] == 3
    cases = client.get(f"/api/v1/cases/?customer_id={c['id']}").json()
    assert len(cases) == 3

def test_case_alert_linkage(client):
    t = client.post("/api/v1/tenants/", json={"name": "T8", "slug": "t8"}).json()
    c = client.post("/api/v1/customers/", json={"name": "C8", "tenant_id": t["id"]}).json()
    alert = client.post("/api/v1/alerts/ingest", json={
        "customer_id": c["id"],
        "source": "wazuh",
        "rule_description": "Brute force attempt",
        "rule_level": 14,
        "raw_data": {"rule": {"level": 14}, "agent": {}}
    }).json()
    auto = client.post(f"/api/v1/cases/auto-create/{c['id']}")
    assert auto.json()["created"] == 1
    updated_alert = client.get(f"/api/v1/alerts/{alert['id']}").json()
    assert updated_alert["case_id"] is not None
    assert updated_alert["status"] == "acknowledged"

def test_alert_status_update(client):
    t = client.post("/api/v1/tenants/", json={"name": "T9", "slug": "t9"}).json()
    c = client.post("/api/v1/customers/", json={"name": "C9", "tenant_id": t["id"]}).json()
    alert = client.post("/api/v1/alerts/ingest", json={"customer_id": c["id"], "source": "wazuh"}).json()
    resp = client.patch(f"/api/v1/alerts/{alert['id']}/status?new_status=investigating")
    assert resp.json()["status"] == "investigating"

def test_case_status_update(client):
    t = client.post("/api/v1/tenants/", json={"name": "T10", "slug": "t10"}).json()
    c = client.post("/api/v1/customers/", json={"name": "C10", "tenant_id": t["id"]}).json()
    case = client.post("/api/v1/cases/", json={"title": "Test", "customer_id": c["id"]}).json()
    resp = client.patch(f"/api/v1/cases/{case['id']}/status?new_status=resolved")
    assert resp.json()["status"] == "resolved"

def test_alert_list_filtering(client):
    t = client.post("/api/v1/tenants/", json={"name": "T11", "slug": "t11"}).json()
    c = client.post("/api/v1/customers/", json={"name": "C11", "tenant_id": t["id"]}).json()
    for sev in ["low", "high", "high", "critical"]:
        client.post("/api/v1/alerts/ingest", json={
            "customer_id": c["id"],
            "source": "wazuh",
            "raw_data": {"rule": {"level": 5 if sev == "low" else 15 if sev == "high" else 20}, "agent": {}}
        })
    high_alerts = client.get(f"/api/v1/alerts/?customer_id={c['id']}&severity=high").json()
    assert len(high_alerts) == 2
