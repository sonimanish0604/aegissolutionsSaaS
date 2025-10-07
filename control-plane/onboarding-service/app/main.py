from fastapi import FastAPI
from app.api.v1.routes_tenants import router as tenants_router
from app.api.v1.routes_webhooks import router as webhooks_router

app = FastAPI(title="Aegis Onboarding Service")

@app.get("/healthz")
async def healthz():
    return {"ok": True}

app.include_router(tenants_router, prefix="/api/v1", tags=["tenants"])
app.include_router(webhooks_router, prefix="/api/v1", tags=["webhooks"])