"""Pydantic schemas for Tenant, Customer, Environment."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Tenant Schemas ──────────────────────────────────────────────────────────

class TenantBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=100, pattern=r'^[a-z0-9-]+$')
    plan: str = Field(default="starter")
    is_active: bool = True


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None


class TenantResponse(TenantBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Customer Schemas ─────────────────────────────────────────────────────────

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    domain: Optional[str] = None
    contact_email: Optional[str] = None
    industry: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    tenant_id: UUID


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    contact_email: Optional[str] = None
    industry: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Environment Schemas ───────────────────────────────────────────────────────

class EnvironmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    env_type: str = Field(default="production")
    wazuh_manager_url: Optional[str] = None
    thehive_url: Optional[str] = None
    misp_url: Optional[str] = None
    is_active: bool = True


class EnvironmentCreate(EnvironmentBase):
    customer_id: UUID


class EnvironmentUpdate(BaseModel):
    name: Optional[str] = None
    env_type: Optional[str] = None
    wazuh_manager_url: Optional[str] = None
    thehive_url: Optional[str] = None
    misp_url: Optional[str] = None
    is_active: Optional[bool] = None


class EnvironmentResponse(EnvironmentBase):
    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
