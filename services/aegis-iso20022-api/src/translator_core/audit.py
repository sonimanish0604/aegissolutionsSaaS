import time, hashlib, json
from dataclasses import dataclass, asdict

@dataclass
class AuditRecord:
    correlation_id: str
    source_mt: str
    target_mx: str
    mapping_profile: str
    xsd_version: str
    mapped_count: int
    error_count: int
    validation_ok: bool
    latency_ms: float
    details: dict | None = None
    xml_validator: str | None = None

def new_correlation_id(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def to_json(record: AuditRecord) -> str:
    return json.dumps(asdict(record), ensure_ascii=False)
