import os, json, asyncio, pytest
from httpx import AsyncClient
from redis.asyncio import Redis
from starlette.responses import JSONResponse
from fastapi import FastAPI

from app.audit.middleware import AuditMiddleware

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
STREAM = "audit:test"

@pytest.mark.asyncio
async def test_audit_middleware_emits(monkeypatch):
    # isolate to a test stream
    monkeypatch.setenv("AUDIT_STREAM_KEY", STREAM)

    app = FastAPI()
    app.add_middleware(AuditMiddleware)

    @app.post("/do")
    async def do():
        return JSONResponse({"ok": True}, status_code=201)

    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.post("/do", headers={"x-correlation-id":"t1"})
        assert r.status_code == 201

    # read from Redis
    rds = Redis.from_url(REDIS_URL, decode_responses=True)
    entries = await rds.xrevrange(STREAM, count=1)
    assert entries, "no audit event written"
    _id, data = entries[0]
    evt = json.loads(data["json"])
    assert evt["method"] == "POST"
    assert evt["path"] == "/do"
    assert evt["status_code"] == 201
    assert "emitted_at" in evt