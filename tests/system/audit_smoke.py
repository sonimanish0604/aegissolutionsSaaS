"""End-to-end smoke test for Docker Compose stack."""

import json
import os
import sys
import time
from pathlib import Path

import boto3
import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_PATH = REPO_ROOT / "services" / "aegis-iso20022-api" / "tests"
if str(TESTS_PATH) not in sys.path:
    sys.path.append(str(TESTS_PATH))

from category1_samples import CATEGORY1_SAMPLES  # type: ignore  # noqa: E402

MT_SAMPLE = CATEGORY1_SAMPLES["MT103"]
TRANSLATOR_URL = os.getenv("TRANSLATOR_URL", "http://localhost:8080")
PREVALIDATOR_URL = os.getenv("PREVALIDATOR_URL", "http://localhost:8081")
S3_ENDPOINT = os.getenv("S3_ENDPOINT_URL", "http://localhost:4566")
AUDIT_BUCKET = os.getenv("AUDIT_S3_BUCKET", "audit-manifests")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")


def wait_for(url: str, timeout: int = 60) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(2)
    raise RuntimeError(f"Service at {url} did not become ready")


def call_prevalidator(session: requests.Session) -> None:
    payload = {"mt_raw": MT_SAMPLE["mt_raw"], "force_type": MT_SAMPLE.get("force_type")}
    resp = session.post(f"{PREVALIDATOR_URL}/prevalidate", json=payload, timeout=10)
    resp.raise_for_status()


def call_translator(session: requests.Session) -> None:
    payload = {
        "mt_raw": MT_SAMPLE["mt_raw"],
        "force_type": MT_SAMPLE.get("force_type"),
        "prevalidate": True,
    }
    resp = session.post(f"{TRANSLATOR_URL}/translate", json=payload, timeout=15)
    resp.raise_for_status()


def list_manifests() -> list[str]:
    session = boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    try:
        resp = session.list_objects_v2(Bucket=AUDIT_BUCKET, Prefix="manifests/")
    except session.exceptions.NoSuchBucket:
        return []
    contents = resp.get("Contents", [])
    return [item["Key"] for item in contents]


def main() -> None:
    wait_for(f"{TRANSLATOR_URL}/")
    wait_for(f"http://localhost:8081/")

    session = requests.Session()
    for _ in range(10):
        call_prevalidator(session)
        call_translator(session)

    deadline = time.time() + 60
    manifests = []
    while time.time() < deadline:
        manifests = list_manifests()
        if len(manifests) >= 3:
            break
        time.sleep(2)

    if len(manifests) < 3:
        raise RuntimeError(f"Expected at least 3 manifest objects, found {len(manifests)}")

    print(f"Audit smoke test passed with manifests: {manifests[:3]}")


if __name__ == "__main__":
    main()
