"""SOCAI Platform - FastAPI Main Entry Point
Module 1: Tenant & Customer Management Foundation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import tenants, customers, environments
from app.database import engine, Base

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SOCAI Platform API",
    description="AI-Native Managed SOC Platform - Tenant & Customer Management",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(environments.router, prefix="/api/v1/environments", tags=["Environments"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "socai-platform", "version": "0.1.0"}
