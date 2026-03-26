import os
import pathlib

BASE = pathlib.Path('/workspaces/socai')

files = {}

# ============================================================
# MODULE 2: Asset & Log Source Model
# ============================================================
files['backend/app/models/asset.py'] = '''
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid, enum as pyenum
from backend.app.database import Base

class AssetType(str, pyenum.Enum):
    server = "server"
    workstation = "workstation"
    network_device = "network_device"
    cloud_resource = "cloud_resource"
    iot = "iot"
    other = "other"

class Asset(Base):
    __tablename__ = "assets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)
    hostname = Column(String(255), nullable=True)
    asset_type = Column(String(50), default="server")
    os_type = Column(String(100), nullable=True)
    criticality = Column(String(20), default="medium")
    is_active = Column(Boolean, default=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    environment_id = Column(UUID(as_uuid=True), ForeignKey("environments.id"), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
'''

# ============================================================
# MODULE 2: Alert Model (for Wazuh ingestion)
# ============================================================
files['backend/app/models/alert.py'] = '''
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from backend.app.database import Base

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(255), nullable=True, index=True)
    source = Column(String(50), default="wazuh")
    raw_data = Column(JSON, nullable=True)
    agent_id = Column(String(50), nullable=True)
    agent_name = Column(String(255), nullable=True)
    agent_ip = Column(String(45), nullable=True)
    rule_id = Column(String(50), nullable=True)
    rule_description = Column(Text, nullable=True)
    rule_level = Column(Integer, default=0)
    rule_groups = Column(JSON, nullable=True)
    mitre_ids = Column(JSON, nullable=True)
    severity = Column(String(20), default="low")
    status = Column(String(30), default="new")
    normalized = Column(Boolean, default=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
'''

# ============================================================
# MODULE 5: Case Model
# ============================================================
files['backend/app/models/case.py'] = '''
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from backend.app.database import Base

class Case(Base):
    __tablename__ = "cases"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), default="low")
    status = Column(String(30), default="open")
    priority = Column(String(20), default="medium")
    assigned_to = Column(String(255), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    alert_count = Column(Integer, default=0)
    mitre_tactics = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
'''

# ============================================================
# Updated models __init__.py
# ============================================================
files['backend/app/models/__init__.py'] = '''
from backend.app.models.tenant import Tenant, Customer, Environment
from backend.app.models.asset import Asset
from backend.app.models.alert import Alert
from backend.app.models.case import Case
'''

# ============================================================
# Schema: Asset
# ============================================================
files['backend/app/schemas/asset.py'] = '''
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class AssetCreate(BaseModel):
    name: str
    customer_id: uuid.UUID
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    asset_type: Optional[str] = "server"
    os_type: Optional[str] = None
    criticality: Optional[str] = "medium"
    environment_id: Optional[uuid.UUID] = None
    description: Optional[str] = None

class AssetOut(BaseModel):
    id: uuid.UUID
    name: str
    customer_id: uuid.UUID
    ip_address: Optional[str]
    hostname: Optional[str]
    asset_type: str
    os_type: Optional[str]
    criticality: str
    is_active: bool
    environment_id: Optional[uuid.UUID]
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    class Config:
        from_attributes = True
'''

# ============================================================
# Schema: Alert
# ============================================================
files['backend/app/schemas/alert.py'] = '''
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
import uuid

class AlertIngest(BaseModel):
    customer_id: uuid.UUID
    source: Optional[str] = "wazuh"
    raw_data: Optional[Dict[str, Any]] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    agent_ip: Optional[str] = None
    rule_id: Optional[str] = None
    rule_description: Optional[str] = None
    rule_level: Optional[int] = 0
    rule_groups: Optional[List[str]] = None
    mitre_ids: Optional[List[str]] = None
    timestamp: Optional[datetime] = None

class AlertOut(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    source: str
    agent_id: Optional[str]
    agent_name: Optional[str]
    agent_ip: Optional[str]
    rule_id: Optional[str]
    rule_description: Optional[str]
    rule_level: int
    severity: str
    status: str
    normalized: bool
    mitre_ids: Optional[List[str]]
    asset_id: Optional[uuid.UUID]
    case_id: Optional[uuid.UUID]
    timestamp: Optional[datetime]
    created_at: Optional[datetime]
    class Config:
        from_attributes = True
'''

# ============================================================
# Schema: Case
# ============================================================
files['backend/app/schemas/case.py'] = '''
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class CaseCreate(BaseModel):
    title: str
    customer_id: uuid.UUID
    description: Optional[str] = None
    severity: Optional[str] = "low"
    priority: Optional[str] = "medium"
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None

class CaseOut(BaseModel):
    id: uuid.UUID
    title: str
    customer_id: uuid.UUID
    description: Optional[str]
    severity: str
    status: str
    priority: str
    assigned_to: Optional[str]
    alert_count: int
    mitre_tactics: Optional[List[str]]
    tags: Optional[List[str]]
    resolved_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    class Config:
        from_attributes = True
'''

# ============================================================
# API: Assets
# ============================================================
files['backend/app/api/v1/assets.py'] = '''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from backend.app.database import get_db
from backend.app.models.asset import Asset
from backend.app.models.tenant import Customer
from backend.app.schemas.asset import AssetCreate, AssetOut

router = APIRouter(prefix="/assets", tags=["assets"])

@router.post("/", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    asset = Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

@router.get("/", response_model=List[AssetOut])
def list_assets(customer_id: Optional[uuid.UUID] = None, db: Session = Depends(get_db)):
    q = db.query(Asset)
    if customer_id:
        q = q.filter(Asset.customer_id == customer_id)
    return q.all()

@router.get("/{asset_id}", response_model=AssetOut)
def get_asset(asset_id: uuid.UUID, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: uuid.UUID, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset)
    db.commit()
'''

# ============================================================
# MODULE 4: Alert Normalization Engine
# ============================================================
files['backend/app/services/normalization.py'] = '''
from typing import Dict, Any, Optional

SEVERITY_MAP = {
    range(0, 4): "informational",
    range(4, 8): "low",
    range(8, 12): "medium",
    range(12, 16): "high",
}

def map_severity(rule_level: int) -> str:
    for r, sev in SEVERITY_MAP.items():
        if rule_level in r:
            return sev
    return "critical" if rule_level >= 16 else "low"

def normalize_wazuh_alert(raw: Dict[str, Any]) -> Dict[str, Any]:
    rule = raw.get("rule", {})
    agent = raw.get("agent", {})
    level = int(rule.get("level", 0))
    mitre = rule.get("mitre", {})
    mitre_ids = mitre.get("id", []) if isinstance(mitre, dict) else []
    groups = rule.get("groups", [])
    return {
        "external_id": raw.get("id"),
        "agent_id": str(agent.get("id", "")),
        "agent_name": agent.get("name"),
        "agent_ip": agent.get("ip"),
        "rule_id": str(rule.get("id", "")),
        "rule_description": rule.get("description"),
        "rule_level": level,
        "rule_groups": groups,
        "mitre_ids": mitre_ids,
        "severity": map_severity(level),
        "normalized": True,
    }

def normalize_alert(source: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    if source == "wazuh":
        return normalize_wazuh_alert(raw)
    return {"normalized": False, "severity": "low"}
'''

# ============================================================
# MODULE 3: Alert Ingest API
# ============================================================
files['backend/app/api/v1/alerts.py'] = '''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from backend.app.database import get_db
from backend.app.models.alert import Alert
from backend.app.models.tenant import Customer
from backend.app.schemas.alert import AlertIngest, AlertOut
from backend.app.services.normalization import normalize_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.post("/ingest", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
def ingest_alert(payload: AlertIngest, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    data = payload.model_dump()
    if data.get("raw_data"):
        normalized = normalize_alert(data.get("source", "wazuh"), data["raw_data"])
        data.update(normalized)
    alert = Alert(**data)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

@router.get("/", response_model=List[AlertOut])
def list_alerts(
    customer_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Alert)
    if customer_id:
        q = q.filter(Alert.customer_id == customer_id)
    if status:
        q = q.filter(Alert.status == status)
    if severity:
        q = q.filter(Alert.severity == severity)
    return q.order_by(Alert.created_at.desc()).all()

@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: uuid.UUID, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.patch("/{alert_id}/status")
def update_alert_status(alert_id: uuid.UUID, new_status: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    valid_statuses = ["new", "acknowledged", "investigating", "resolved", "false_positive"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {valid_statuses}")
    alert.status = new_status
    db.commit()
    db.refresh(alert)
    return alert
'''

# ============================================================
# MODULE 5: Case Creation Service (auto-case from alerts)
# ============================================================
files['backend/app/services/case_engine.py'] = '''
from sqlalchemy.orm import Session
from backend.app.models.alert import Alert
from backend.app.models.case import Case
import uuid

def create_case_from_alert(alert: Alert, db: Session) -> Case:
    mitre = alert.mitre_ids or []
    case = Case(
        title=f"[AUTO] {alert.rule_description or alert.rule_id or alert.source}",
        description=f"Auto-generated case from alert {alert.id}. Agent: {alert.agent_name}. Rule: {alert.rule_description}",
        severity=alert.severity,
        status="open",
        priority="medium" if alert.severity in ["low", "informational"] else "high",
        customer_id=alert.customer_id,
        alert_count=1,
        mitre_tactics=mitre,
        tags=[alert.source, f"rule:{alert.rule_id}"] if alert.rule_id else [alert.source],
    )
    db.add(case)
    db.flush()
    alert.case_id = case.id
    alert.status = "acknowledged"
    db.commit()
    db.refresh(case)
    return case

def auto_case_high_severity(db: Session, customer_id) -> list:
    uncased_high = db.query(Alert).filter(
        Alert.customer_id == customer_id,
        Alert.case_id == None,
        Alert.severity.in_(["high", "critical"]),
        Alert.status == "new"
    ).all()
    cases = []
    for alert in uncased_high:
        c = create_case_from_alert(alert, db)
        cases.append(c)
    return cases
'''

# ============================================================
# MODULE 5: Cases API
# ============================================================
files['backend/app/api/v1/cases.py'] = '''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from backend.app.database import get_db
from backend.app.models.case import Case
from backend.app.models.tenant import Customer
from backend.app.schemas.case import CaseCreate, CaseOut
from backend.app.services.case_engine import auto_case_high_severity

router = APIRouter(prefix="/cases", tags=["cases"])

@router.post("/", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    case = Case(**payload.model_dump())
    db.add(case)
    db.commit()
    db.refresh(case)
    return case

@router.get("/", response_model=List[CaseOut])
def list_cases(
    customer_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Case)
    if customer_id:
        q = q.filter(Case.customer_id == customer_id)
    if status:
        q = q.filter(Case.status == status)
    return q.order_by(Case.created_at.desc()).all()

@router.get("/{case_id}", response_model=CaseOut)
def get_case(case_id: uuid.UUID, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.patch("/{case_id}/status")
def update_case_status(case_id: uuid.UUID, new_status: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    valid = ["open", "investigating", "resolved", "closed", "false_positive"]
    if new_status not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose: {valid}")
    case.status = new_status
    db.commit()
    db.refresh(case)
    return case

@router.post("/auto-create/{customer_id}")
def auto_create_cases(customer_id: uuid.UUID, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    cases = auto_case_high_severity(db, customer_id)
    return {"created": len(cases), "case_ids": [str(c.id) for c in cases]}
'''

# ============================================================
# Updated main.py with all routers
# ============================================================
files['backend/app/main.py'] = '''
from fastapi import FastAPI
from backend.app.database import Base, engine
from backend.app.api.v1 import tenants, customers, environments, assets, alerts, cases

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SOC AI Platform", version="0.3.0", description="AI-Native Managed SOC")

app.include_router(tenants.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(environments.router, prefix="/api/v1")
app.include_router(assets.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(cases.router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "socai", "version": "0.3.0"}
'''

# Services __init__
files['backend/app/services/__init__.py'] = ''

# Updated schemas __init__
files['backend/app/schemas/__init__.py'] = '''
from backend.app.schemas.tenant import TenantCreate, TenantOut, CustomerCreate, CustomerOut, EnvironmentCreate, EnvironmentOut
from backend.app.schemas.asset import AssetCreate, AssetOut
from backend.app.schemas.alert import AlertIngest, AlertOut
from backend.app.schemas.case import CaseCreate, CaseOut
'''

# Updated api v1 __init__
files['backend/app/api/v1/__init__.py'] = ''

# ============================================================
# Comprehensive Test File for Modules 2-5
# ============================================================
files['tests/test_module2_5_all.py'] = '''
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
'''

# ============================================================
# WRITE ALL FILES
# ============================================================
print(f"Creating {len(files)} files...")
for path, content in files.items():
    full_path = BASE / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)
    print(f"  ✓ {path}")
print("\nAll files created successfully!")
print("Next steps:")
print("1. pip install -q pytest httpx fastapi sqlalchemy")
print("2. python -m pytest tests/ -v")
