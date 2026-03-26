
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
