# app/main.py
import logging, os
from fastapi import FastAPI
from opentelemetry import trace
from app.deps.telemetry import init_otel
from app.audit.middleware import AuditMiddleware

app = FastAPI(title="Aegis Onboarding Service")

#app.audit.add_middleware(AuditMiddleware)
app.add_middleware(AuditMiddleware)

init_otel()
tracer = trace.get_tracer("onboarding.healthz")

@app.get("/healthz", tags=["default"])
def healthz():
    with tracer.start_as_current_span("healthz-check") as span:
        payload = {
            "event.type": "healthz.check",
            "event.outcome": "success",
            "actor.system": "probe",
            "http.target": "/healthz",
        }
        for k, v in payload.items():
            span.set_attribute(k, v)
        logging.getLogger("onboarding.audit").info("healthz ok", extra=payload)
        return {"status": "ok"}

# Include DB-dependent routers only when DB URL exists
if os.getenv("DATABASE_URL_ASYNC"):
    from app.api.v1.routes_tenants import router as tenants_router
    from app.api.v1.routes_webhooks import router as webhooks_router
    app.include_router(tenants_router,  prefix="/api/v1", tags=["tenants"])
    app.include_router(webhooks_router, prefix="/api/v1", tags=["webhooks"])
else:
    logging.getLogger(__name__).warning(
        "DATABASE_URL_ASYNC not set; skipping tenants/webhooks routers"
    )