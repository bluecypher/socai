
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
