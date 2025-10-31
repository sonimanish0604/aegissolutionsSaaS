from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .hashing import hash_bytes, hash_json, hash_text


@dataclass
class AuditEvent:
    """Canonical audit event payload for downstream audit pipeline."""

    v: str = "1.0"
    type: str = "api_call"
    ts: str = ""
    tenant_id: str = ""
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "v": self.v,
            "type": self.type,
            "ts": self.ts,
            "tenant_id": self.tenant_id,
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
