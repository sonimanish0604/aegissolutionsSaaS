from __future__ import annotations

import base64
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from audit_integrity import ManifestBuilder, ManifestObject  # noqa: E402  pylint: disable=wrong-import-position


def test_manifest_builder_creates_deterministic_hash():
    builder = ManifestBuilder(created_by="aws-kafka-connect")
    objs = [
        ManifestObject(key="a", size=10, sha256="abc"),
        ManifestObject(key="b", size=20, sha256="def"),
    ]
    manifest = builder.build(partition="dt=2025/10/30/04/tenant_id=TEN123", objects=objs)
    assert manifest.aggregate_sha256 == builder._aggregate_hash(objs)  # type: ignore[attr-defined]
    again = builder.build(partition="dt=2025/10/30/04/tenant_id=TEN123", objects=objs)
    assert manifest.aggregate_sha256 == again.aggregate_sha256


def test_manifest_signature_uses_hmac_sha256():
    builder = ManifestBuilder(created_by="aws-kafka-connect")
    manifest = builder.build("partition", [ManifestObject("f", 100, "sha")])
    assert manifest.created_by == "aws-kafka-connect"
    signature = builder.sign(manifest, b"secret")
    decoded = base64.b64decode(signature)
    assert len(decoded) == 32
