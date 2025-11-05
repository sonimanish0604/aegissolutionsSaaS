from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

try:
    import ulid  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback path for local tooling
    ulid = None  # type: ignore
    import uuid

from .hashing import hash_bytes, hash_json, hash_text


def _generate_event_id() -> str:
    if ulid is not None:
        return ulid.new().str  # type: ignore[attr-defined]
    return uuid.uuid4().hex
@dataclass
class AuditEvent:
    """Canonical audit event payload for downstream audit pipeline."""

    v: str = "1.0"
    type: str = "api_call"
    ts: str = ""
    tenant_id: str = ""
    tenant_uuid: str = ""
    event_id: str = ""
    attempt: int = 1
    x_request_id: str = ""
    route: str = ""
    result: str = "accepted"
    counts: Dict[str, int] = field(default_factory=dict)
    ids: Dict[str, Optional[str]] = field(default_factory=dict)
    mx: Dict[str, Optional[str]] = field(default_factory=dict)
    hash: Dict[str, str] = field(default_factory=dict)
    versions: Dict[str, str] = field(default_factory=dict)
    timing_ms: Dict[str, int] = field(default_factory=dict)
    severity: str = "info"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def with_hash(self, key: str, value: Any) -> "AuditEvent":
        """Attach a SHA-256 hash for the provided content."""
        if isinstance(value, (bytes, bytearray)):
            digest = hash_bytes(value)
        elif isinstance(value, str):
            digest = hash_text(value)
        else:
            digest = hash_json(value)
        self.hash[key] = digest
        return self

    def ensure_event_id(self) -> "AuditEvent":
        """Populate event_id if it has not been set."""
        if not self.event_id:
            self.event_id = _generate_event_id()
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "v": self.v,
            "type": self.type,
            "ts": self.ts,
            "tenant_id": self.tenant_id,
            "tenant_uuid": self.tenant_uuid,
            "event_id": self.event_id,
            "attempt": self.attempt,
            "x_request_id": self.x_request_id,
            "route": self.route,
            "result": self.result,
            "counts": self.counts,
            "ids": self.ids,
            "mx": self.mx,
            "hash": self.hash,
            "versions": self.versions,
            "timing_ms": self.timing_ms,
            "severity": self.severity,
            "metadata": self.metadata,
        }
