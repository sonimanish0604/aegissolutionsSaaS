# Audit Pipeline Blueprint

This document captures the end-to-end flow for the Aegis audit trail. It focuses on the immutable archive path (Kafka → S3 Parquet with signed manifests) and the supporting components required in each environment.

## Event schema

Application code produces a compact, PII-free JSON record. `services/aegis-iso20022-api/src/audit_event/model.py` contains the canonical dataclass; the generated payload lines up with the contract below:

```json
{
  "v": "1.0",
  "type": "api_call | batch | message",
  "ts": "2025-10-30T02:10:05.123Z",
  "tenant_id": "TEN123",
  "tenant_uuid": "41cd45b3-95da-4550-a793-ce9fefb39c8e",
  "event_id": "01HEZ3YD1K5M1K2TBYY63SZ8CD",
  "attempt": 1,
  "x_request_id": "8f2e5b2e-3b5c-47c5-82e0-7f1b9e2a2e8f",
  "route": "/translate",
  "result": "accepted | rejected | partial",
  "counts": {"in": 250, "valid": 245, "failed": 5},
  "ids": {"batch_id": "...", "message_id": "...", "mt_trn_ref": "...", "uetr": null},
  "mx": {"type": "pacs.008.001.13", "biz_msg_idr": "...", "end_to_end_id": "..."},
  "hash": {
    "payload": "sha256:...",
    "mt": "sha256:...",
    "mx": "sha256:..."
  },
  "versions": {"ruleset": "MT103-NV-1.7.0", "mapping": "MT103→pacs.008 v0.9.2"},
  "timing_ms": {"validate": 12, "transform": 830, "total": 860},
  "severity": "info",
  "metadata": {"method": "POST", "status_code": 200}
}
```

Hash helpers (`hash_bytes`, `hash_text`, `hash_json`) provide normalized SHA-256 digests to satisfy tamper-evidence requirements.

## Transport

1. **Application** – FastAPI middleware (`audit_middleware.AuditMiddleware`) captures every request, enriches `AuditEvent`, and submits it to an emitter instance.
2. **Emitters** – the codebase ships with:
   - `LoggingEmitter` – writes JSON into structured logs (default for local dev/tests).
   - `KafkaAuditEmitter` – pushes events to Kafka using `kafka-python`. It keys messages by tenant so a sink can partition efficiently.
   - `NoopEmitter` – drops events (useful for offline tests).
3. **Kafka** – authoritative topic: `audit.events`
   - Producer headers: `event_id` (ULID) and `schema_version` (future use).
   - Dead-letter topic: `audit.events.dlq` (malformed payloads, serialization errors).

## S3 archive sink

Target layout:

```
s3://aegis-audit-archive/
  dt=YYYY/MM/DD/HH/tenant_id=TEN123/part-0000.parquet
  dt=YYYY/MM/DD/HH/tenant_id=TEN789/part-0001.parquet
  manifests/2025/10/30/04/MANIFEST.json
  manifests/2025/10/30/04/MANIFEST.sig
```

Recommended Kafka Connect configuration (Confluent S3 sink) – adapt secrets at deployment time:

```json
{
  "name": "audit-s3-sink",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "2",
    "topics": "audit.events",
    "s3.bucket.name": "aegis-audit-archive",
    "s3.part.size": "5242880",
    "s3.region": "us-east-1",

    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",

    "flush.size": "5000",
    "rotate.interval.ms": "600000",
    "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
    "path.format": "dt=yyyy/MM/dd/HH/tenant_id=${record:value.tenant_id}",
    "partition.duration.ms": "3600000",
    "timestamp.extractor": "RecordField",
    "timestamp.field": "ts",

    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",

    "behavior.on.null.values": "ignore",
    "behavior.on.malformed.documents": "ignore",

    "aws.access.key.id": "${file:/opt/secrets/aws.properties:AWS_ACCESS_KEY_ID}",
    "aws.secret.access.key": "${file:/opt/secrets/aws.properties:AWS_SECRET_ACCESS_KEY}"
  }
}
```

Follow-on serverless components:

- **Manifest Builder** – hourly Lambda/container that collects the Parquet keys for a partition, writes `MANIFEST.json`, signs it (`MANIFEST.sig`) via KMS/HSM. Consumers can verify completeness by replaying the manifest. The repository includes a helper implementation at `services/aegis-iso20022-api/src/audit_integrity/manifest.py` used for integration tests and tooling.
- **Athena** – external tables over the bucket allow ad-hoc SQL for investigations. Enable S3 Object Lock (Compliance mode) + lifecycle to Glacier for long-term retention.
- **Optional sinks** – SIEM connector / OpenSearch sink can subscribe directly to Kafka for near real-time operations. S3 remains the system of record.

## Local development checklist

1. Enable the middleware in the FastAPI app (wire `AuditMiddleware` with the desired emitter). Logging emitter is default-safe.
2. Run unit tests:
   ```bash
   pytest services/aegis-iso20022-api/tests/test_audit_event_model.py services/aegis-iso20022-api/tests/test_audit_middleware.py -q
   pytest services/aegis-iso20022-api/tests/test_kafka_emitter.py -q
   ```
3. When Kafka is available locally (e.g., docker-compose), set the appropriate environment variable to switch to `KafkaAuditEmitter` and produce sample records for integration testing.

## Deployment notes

- Inject tenant metadata (UUID, ID) at the ingress layer so middleware can populate the event without touching message payloads.
- Ensure the Kafka producer credentials are scoped to the `audit.events` topic only.
- Configure alerting on Kafka lag and DLQ growth. A stuck sink must be triaged before compliance SLAs are impacted.
- Lock down the S3 bucket with Object Lock, bucket policies, and access logging. Set retention per regulatory requirements (e.g., 7 years).

This blueprint aligns the service implementation with the audit requirements and provides the configuration hooks needed to stand up the downstream pipeline.
