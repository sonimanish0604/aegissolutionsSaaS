import json
import logging
import os
import time
from collections import deque
from hashlib import sha256
from typing import Deque, Dict, Optional
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
from kafka import KafkaConsumer

from audit_integrity.manifest import ManifestBuilder, ManifestObject
from audit_integrity.signer import KmsSigner, LocalHmacSigner

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("audit-worker")

BATCH_SIZE = int(os.getenv("AUDIT_MANIFEST_BATCH", "3"))


def _resolve_signer() -> LocalHmacSigner:
    kms_key = os.getenv("AUDIT_KMS_KEY_ID")
    region = os.getenv("AWS_REGION", "us-east-1")
    if kms_key:
        kms_client = boto3.client("kms", region_name=region)
        return KmsSigner(kms_client, kms_key)
    secret = os.getenv("LOCAL_SIGNING_SECRET", "audit-dev-secret").encode("utf-8")
    return LocalHmacSigner(secret)


def _s3_client(bucket: Optional[str]):
    if not bucket:
        return None
    region = os.getenv("AWS_REGION", "us-east-1")
    endpoint = os.getenv("S3_ENDPOINT_URL")
    kwargs = {"region_name": region}
    if endpoint:
        kwargs["endpoint_url"] = endpoint
    session = boto3.client("s3", **kwargs)
    try:
        params = {}
        if region != "us-east-1":
            params = {"CreateBucketConfiguration": {"LocationConstraint": region}}
        session.create_bucket(Bucket=bucket, **params)
    except session.exceptions.BucketAlreadyExists:
        pass
    except session.exceptions.BucketAlreadyOwnedByYou:
        pass
    except ClientError as exc:
        logger.warning("Could not ensure bucket %s: %s", bucket, exc)
    return session


def main() -> None:
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
    topic = os.getenv("AUDIT_TOPIC", "audit.events")
    group_id = os.getenv("AUDIT_GROUP_ID", "aegis-audit-worker")
    auto_offset = os.getenv("KAFKA_OFFSET_RESET", "earliest")

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap,
        enable_auto_commit=True,
        auto_offset_reset=auto_offset,
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
    )

    signer = _resolve_signer()
    builder = ManifestBuilder(created_by=os.getenv("MANIFEST_CREATED_BY", "aegis-audit-worker"))
    bucket = os.getenv("AUDIT_S3_BUCKET")
    s3_client = _s3_client(bucket)

    buffer: Deque[Dict] = deque()
    total_events = 0
    manifest_batches = 0

    def flush_buffer(force: bool = False):
        nonlocal manifest_batches
        while len(buffer) >= BATCH_SIZE or (force and buffer):
            chunk_size = BATCH_SIZE if len(buffer) >= BATCH_SIZE else len(buffer)
            manifest_batches += 1
            batch = [buffer.popleft() for _ in range(chunk_size)]
            objects = [
                ManifestObject(
                    key=item["key"],
                    size=item["size"],
                    sha256=item["sha256"],
                )
                for item in batch
            ]
            manifest = builder.build(partition=f"batch-{manifest_batches}", objects=objects)
            signature = builder.sign(manifest, signer)
            envelope = {
                "manifest": manifest.to_dict(),
                "signature": signature,
                "events": [item["payload"] for item in batch],
            }
            payload = json.dumps(envelope).encode("utf-8")

            if bucket and s3_client:
                key = f"manifests/batch-{manifest_batches}-{int(time.time())}.json"
                s3_client.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=payload,
                    ContentType="application/json",
                )
                logger.info("Persisted manifest #%s to s3://%s/%s", manifest_batches, bucket, key)
            else:
                logger.info("Manifest #%s generated (no bucket configured)", manifest_batches)

    logger.info("Audit worker listening on topic %s", topic)
    for record in consumer:
        payload_dict = record.value
        raw_bytes = json.dumps(payload_dict).encode("utf-8")
        event_id = payload_dict.get("event_id") or str(uuid4())
        buffer.append(
            {
                "key": f"{event_id}-{record.offset}",
                "size": len(raw_bytes),
                "sha256": sha256(raw_bytes).hexdigest(),
                "payload": payload_dict,
            }
        )
        total_events += 1
        logger.info("Processed audit event %s (total=%s, buffer=%s)", event_id, total_events, len(buffer))
        flush_buffer()


if __name__ == "__main__":
    main()
