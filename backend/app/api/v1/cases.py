
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
