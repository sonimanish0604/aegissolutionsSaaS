from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("starlette")

from fastapi import FastAPI  # type: ignore
from fastapi.testclient import TestClient  # type: ignore

CURRENT = Path(__file__).resolve().parent
SRC = CURRENT.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from audit_middleware import AuditMiddleware
from audit_emitter.base import AuditEmitter
from audit_event import AuditEvent
from audit_utils import get_audit_context


class CaptureEmitter(AuditEmitter):
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def emit(self, event: AuditEvent) -> None:
        self.events.append(event)


def build_app(emitter: AuditEmitter) -> FastAPI:
    app = FastAPI()
    app.add_middleware(AuditMiddleware, emitter=emitter)

    @app.get("/ping")
    async def ping():  # pragma: no cover - executed via test client
        ctx = get_audit_context()
        assert ctx["tenant_id"] == "TEN123"
        assert ctx["event_id"]
        assert ctx["attempt"] == 1
        return {"status": "ok"}

    return app


def test_audit_middleware_emits_event():
    emitter = CaptureEmitter()
    app = build_app(emitter)
    client = TestClient(app)

    response = client.get(
        "/ping",
        headers={
            "x-tenant-id": "TEN123",
            "x-tenant-uuid": "UUID-123",
            "x-request-id": "REQ-456",
        },
    )
    assert response.status_code == 200
    assert len(emitter.events) == 1
    payload = emitter.events[0].to_dict()
    assert payload["tenant_id"] == "TEN123"
    assert payload["tenant_uuid"] == "UUID-123"
    assert payload["x_request_id"] == "REQ-456"
    assert payload["route"] == "/ping"
    assert payload["result"] == "accepted"
    assert payload["timing_ms"]["total"] >= 0
    assert payload["event_id"]
    assert len(payload["event_id"]) >= 16
    assert payload["attempt"] == 1
