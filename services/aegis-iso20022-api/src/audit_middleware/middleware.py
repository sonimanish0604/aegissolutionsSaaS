
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Callable, Optional
from uuid import uuid4

import ulid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from audit_event import AuditEvent
from audit_utils import set_audit_context
from audit_emitter.base import AuditEmitter


class AuditMiddleware(BaseHTTPMiddleware):
    """Capture request metadata and emit audit events."""

    def __init__(self, app, emitter: AuditEmitter) -> None:
        super().__init__(app)
        self._emitter = emitter

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        start = time.perf_counter()
        tenant_id = request.headers.get("x-tenant-id", "")
        tenant_uuid = request.headers.get("x-tenant-uuid", "")
        x_request_id = request.headers.get("x-request-id", str(uuid4()))
        incoming_event_id = request.headers.get("x-event-id")
        attempt_header = request.headers.get("x-attempt")
        try:
            attempt = int(attempt_header) if attempt_header else 1
        except ValueError:
            attempt = 1

        event_id = incoming_event_id or ulid.new().str

        set_audit_context(
            {
                "tenant_id": tenant_id,
                "tenant_uuid": tenant_uuid,
                "x_request_id": x_request_id,
                "event_id": event_id,
                "attempt": attempt,
            }
        )

        status_code: Optional[int] = None
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:  # pragma: no cover - re-raised after audit
            status_code = 500
            raise
        finally:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            event = AuditEvent(
                type="api_call",
                ts=datetime.now(timezone.utc).isoformat(),
                tenant_id=tenant_id,
                tenant_uuid=tenant_uuid,
                event_id=event_id,
                attempt=attempt,
                x_request_id=x_request_id,
                route=request.url.path,
                result="accepted" if (status_code or 0) < 400 else "rejected",
                timing_ms={"total": elapsed_ms},
                metadata={"method": request.method, "status_code": status_code},
            ).ensure_event_id()
            self._emitter.emit(event)
