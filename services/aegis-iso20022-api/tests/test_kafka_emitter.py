
from __future__ import annotations

import json

import pytest

from audit_event import AuditEvent
from audit_emitter.kafka import KafkaAuditEmitter


class DummyProducer:
    def __init__(self):
        self.sent = []

    def send(self, topic, value=None, key=None, headers=None):
        self.sent.append((topic, value, key, headers))

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

    topic, payload, key, headers = producer.sent[0]
    assert topic == "audit.events"
    if isinstance(payload, bytes):
        payload_data = json.loads(payload.decode("utf-8"))
    else:
        payload_data = payload
    assert payload_data["tenant_id"] == "TEN123"
    assert payload_data["event_id"]

    key_value = key.decode("utf-8") if isinstance(key, bytes) else key
    assert key_value == "TEN123"

    assert headers is not None
    header_keys = [k for (k, _v) in headers]
    assert "event_id" in header_keys
    assert "schema_version" in header_keys
