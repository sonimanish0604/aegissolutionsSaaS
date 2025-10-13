from fastapi import FastAPI
from fastapi import Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.infra.db_async import get_async_session
from app.api.v1.routes_tenants import router as tenants_router
from app.api.v1.routes_webhooks import router as webhooks_router
from app.audit.middleware import AuditMiddleware
from app.logging_config import setup_logging, CorrelationIdMiddleware



app = FastAPI(title="Aegis Onboarding Service")
setup_logging()


app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(AuditMiddleware)
@app.get("/healthz")
async def healthz():
    return {"ok": True}

app.include_router(tenants_router,  prefix="/api/v1", tags=["tenants"])
app.include_router(webhooks_router, prefix="/api/v1", tags=["webhooks"])
