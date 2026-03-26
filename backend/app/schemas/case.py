
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
