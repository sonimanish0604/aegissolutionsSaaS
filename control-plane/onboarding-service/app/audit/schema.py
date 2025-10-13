from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import Any, Literal, Optional
from uuid import uuid4
from datetime import datetime, timezone
import hashlib, json

SENSITIVE_KEYS = {"password","pass","secret","token","authorization","ssn","dob","email","api_key","set-cookie"}

def _redact(obj: Any) -> Any:
    if obj is None: return None
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k.lower() in SENSITIVE_KEYS:
                out[k] = "***"
            else:
                out[k] = _redact(v)
        return out
    if isinstance(obj, list): return [_redact(x) for x in obj]
    return obj

def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    emitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    service: str
    env: str
    tenant_id: Optional[str] = None
    actor_id: Optional[str] = None
    actor_type: Literal["user","service","system"] = "service"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    request_id: Optional[str] = None
    idempotency_key: Optional[str] = None

    # HTTP
    method: str
    path: str
    status_code: int
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    latency_ms: Optional[int] = None

    # Optional payload/meta (redacted)
    payload: Optional[dict] = None
    payload_hash: Optional[str] = None
    response_size: Optional[int] = None
    request_size: Optional[int] = None

    # integrity (optional)
    checksum: Optional[str] = None

    @field_validator("payload", mode="before")
    @classmethod
    def redact_payload(cls, v):
        return _redact(v)

    def with_body_hash(self, raw_body: bytes | None) -> "AuditEvent":
        if raw_body:
            return self.model_copy(update={
                "request_size": len(raw_body),
                "payload_hash": _sha256_bytes(raw_body),
            })
        return self