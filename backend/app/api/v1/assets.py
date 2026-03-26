
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
