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
        )

    def emit(self, event: AuditEvent) -> None:
        payload = event.to_dict()
        key = payload.get("tenant_id") or payload.get("tenant_uuid")
        self._producer.send(self._topic, value=payload, key=key)

    def flush(self) -> None:
        self._producer.flush()

    def close(self) -> None:
        self._producer.close()
