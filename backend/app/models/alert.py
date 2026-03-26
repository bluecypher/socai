
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
