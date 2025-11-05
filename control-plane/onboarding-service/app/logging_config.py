# app/logging_config.py
from __future__ import annotations
import json, logging, sys
from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send
import uuid
import contextvars

# contextvar for correlation id available to log records
_correlation_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("correlation_id", default=None)

def get_correlation_id() -> str | None:
    return _c_id if (_c_id := _correlation_id.get()) else None

def set_correlation_id(value: str | None) -> None:
    _correlation_id.set(value)

class CorrelationIdMiddleware:
    """Ensures every request has a correlation id and exposes it to logs via contextvars."""
    def __init__(self, app: ASGIApp, header_name: str = "x-correlation-id"):
        self.app = app
        self.header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request = Request(scope, receive=receive)
        cid = request.headers.get(self.header_name)
        if not cid:
            cid = str(uuid.uuid4())
        token = _correlation_id.set(cid)
        try:
            await self.app(scope, receive, send)
        finally:
            _correlation_id.reset(token)

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Standard HTTP-ish extras if provided via LoggerAdapter or logging extra={}
        for k in ("path", "method", "tenant_id", "actor_id", "status_code"):
            if hasattr(record, k):
                data[k] = getattr(record, k)
        # Correlation ID from context
        cid = get_correlation_id()
        if cid:
            data["correlation_id"] = cid
        if record.exc_info:
            data["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))

def setup_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    root.setLevel(level)
    # purge existing handlers (useful during reload)
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)