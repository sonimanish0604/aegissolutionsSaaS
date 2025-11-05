# app/audit/middleware.py
from __future__ import annotations
import os, time
from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send
from app.audit.schema import AuditEvent
from app.audit.adapters import get_cache_stream
from app.logging_config import get_correlation_id

AUDIT_SERVICE = os.getenv("AUDIT_SERVICE", "onboarding-service")
AUDIT_ENV = os.getenv("AUDIT_ENV", "dev")

class AuditMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
        self.stream = get_cache_stream()  # resolved via adapters layer

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope, receive=receive)
        t0 = time.time()
        status_holder = {"code": 500}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_holder["code"] = message["status"]
            await send(message)

        await self.app(scope, receive, send_wrapper)
        latency_ms = int((time.time() - t0) * 1000)

        method = request.method.upper()
        if method not in ("POST", "PUT", "PATCH", "DELETE"):
            return

        evt = AuditEvent(
            service=AUDIT_SERVICE,
            env=AUDIT_ENV,
            tenant_id=request.headers.get("x-tenant-id"),
            actor_id=request.headers.get("x-actor-id"),
            actor_type=request.headers.get("x-actor-type", "service"),
            trace_id=get_correlation_id() or request.headers.get("x-correlation-id"),
            request_id=request.headers.get("x-request-id"),
            idempotency_key=request.headers.get("idempotency-key"),
            method=method,
            path=request.url.path,
            status_code=status_holder["code"],
            ip=(request.client.host if request.client else None),
            user_agent=request.headers.get("user-agent"),
            latency_ms=latency_ms,
            payload=None,  # keep minimal; body hashing handled in schema if needed later
        )

        # fire-and-forget publish; never block or raise
        try:
            await self.stream.publish(evt.model_dump())
        except Exception:
            pass