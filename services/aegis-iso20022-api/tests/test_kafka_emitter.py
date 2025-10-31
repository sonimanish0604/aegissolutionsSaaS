from __future__ import annotations

import json
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from audit_event import AuditEvent
from audit_emitter.kafka import KafkaAuditEmitter


class DummyProducer:
    def __init__(self):
        self.sent = []

    def send(self, topic, value=None, key=None):
        self.sent.append((topic, value, key))

    def flush(self):
        self.sent.append("flush")

    def close(self):
        self.sent.append("close")


def test_kafka_audit_emitter(monkeypatch):
    producer = DummyProducer()
    monkeypatch.setattr("audit_emitter.kafka.KafkaProducer", lambda **_: producer)

    emitter = KafkaAuditEmitter(bootstrap_servers="localhost:9092", topic="audit.events")
    event = AuditEvent(tenant_id="TEN123", route="/ping")
    emitter.emit(event)

    assert producer.sent[0][0] == "audit.events"
    payload = producer.sent[0][1]
    if isinstance(payload, bytes):
        payload_data = json.loads(payload.decode("utf-8"))
    else:
        payload_data = payload
    assert payload_data["tenant_id"] == "TEN123"
    key = producer.sent[0][2]
    if isinstance(key, bytes):
        key_value = key.decode("utf-8")
    else:
        key_value = key
    assert key_value == "TEN123"
