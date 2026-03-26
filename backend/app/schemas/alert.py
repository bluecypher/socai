
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
