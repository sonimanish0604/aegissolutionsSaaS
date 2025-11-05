
from __future__ import annotations

import json
from typing import Optional

from audit_event import AuditEvent
from .base import AuditEmitter

try:
    from kafka import KafkaProducer
except ImportError:
    KafkaProducer = None  # type: ignore


class KafkaAuditEmitter(AuditEmitter):
    """Emit audit events to a Kafka topic."""

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str = "audit.events",
        client_id: str = "aegis-audit-producer",
    ) -> None:
        if KafkaProducer is None:  # pragma: no cover - handled in CI env
            raise RuntimeError("kafka-python is required for KafkaAuditEmitter")
        self._topic = topic
        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            client_id=client_id,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda v: v.encode("utf-8") if v else None,
            acks="all",
            linger_ms=5,
            retries=3,
        )

    def emit(self, event: AuditEvent) -> None:
        prepared = event.ensure_event_id()
        payload = prepared.to_dict()
        key = payload.get("tenant_id") or payload.get("tenant_uuid")
        headers = []
        event_id = payload.get("event_id")
        if event_id:
            headers.append(("event_id", event_id.encode("utf-8")))
        headers.append(("schema_version", payload.get("v", "1.0").encode("utf-8")))
        self._producer.send(self._topic, value=payload, key=key, headers=headers)

    def flush(self) -> None:
        self._producer.flush()

    def close(self) -> None:
        self._producer.close()
