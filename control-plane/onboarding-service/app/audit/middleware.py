# app/middleware.py
from __future__ import annotations
import json
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.audit import write_audit_event
from app.db import async_session_maker

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
ACTOR_TYPE_DEFAULT = "user"  # or "system" for machine calls

async def _read_json_safely(request: Request) -> Optional[dict]:
    try:
        body = await request.body()
        if not body:
            return None
        return json.loads(body.decode("utf-8"))
    except Exception:
        return None

def _reinject_body(request: Request, body: bytes):
    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}
    request._receive = receive  # type: ignore[attr-defined]

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Read the body once; then put it back so downstream can read it
        raw_body = await request.body()
        _reinject_body(request, raw_body)

        # Process request
        response: Response
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            # If handler crashes, still log a 500
            status_code = 500
            raise
        finally:
            # Only audit mutating methods
            if request.method not in SAFE_METHODS:
                try:
                    payload = json.loads(raw_body.decode("utf-8")) if raw_body else None
                except Exception:
                    payload = None

                # Pull common context (customize to your headers)
                tenant_id        = request.headers.get("X-Tenant-Id")
                actor_id         = request.headers.get("X-Actor-Id")
                actor_type       = request.headers.get("X-Actor-Type", ACTOR_TYPE_DEFAULT)
                correlation_id   = request.headers.get("X-Correlation-Id")
                idempotency_key  = request.headers.get("Idempotency-Key")
                user_agent       = request.headers.get("User-Agent")
                source_ip        = request.client.host if request.client else None

                # Derive action (e.g., POST /v1/tenants -> tenants.create)
                route_path = request.url.path
                seg = [s for s in route_path.split("/") if s]
                resource = seg[1] if len(seg) > 1 else seg[0] if seg else ""
                action = {
                    "POST":   f"{resource}.create",
                    "PUT":    f"{resource}.replace",
                    "PATCH":  f"{resource}.update",
                    "DELETE": f"{resource}.delete",
                }.get(request.method, f"{resource}.{request.method.lower()}")

                # Write audit row (synchronously for durability)
                async with async_session_maker() as session:  # type: AsyncSession
                    await write_audit_event(
                        session=session,
                        route=route_path,
                        method=request.method,
                        status_code=status_code,
                        action=action,
                        tenant_id=tenant_id,
                        actor_id=actor_id,
                        actor_type=actor_type,
                        source_ip=source_ip,
                        user_agent=user_agent,
                        correlation_id=correlation_id,
                        idempotency_key=idempotency_key,
                        payload=payload,
                    )
            # else: skip auditing GET/HEAD/OPTIONS

        return response