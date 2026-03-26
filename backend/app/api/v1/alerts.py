
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
