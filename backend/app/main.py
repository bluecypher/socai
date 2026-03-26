
from fastapi import FastAPI
from backend.app.database import Base, engine
from backend.app.api.v1 import tenants, customers, environments, assets, alerts, cases

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SOC AI Platform", version="0.3.0", description="AI-Native Managed SOC")

app.include_router(tenants.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(environments.router, prefix="/api/v1")
app.include_router(assets.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(cases.router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "socai", "version": "0.3.0"}
