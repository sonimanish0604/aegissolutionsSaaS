
from __future__ import annotations

import base64
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Iterable, List


@dataclass(frozen=True)
class ManifestObject:
    key: str
    size: int
    sha256: str

    def to_dict(self) -> dict:
        return {"key": self.key, "size": self.size, "sha256": self.sha256}


@dataclass
class Manifest:
    version: str
    created_at: str
    partition: str
    objects: List[ManifestObject]
    aggregate_sha256: str
    created_by: str

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "created_at": self.created_at,
            "partition": self.partition,
            "objects": [obj.to_dict() for obj in self.objects],
            "aggregate_sha256": self.aggregate_sha256,
            "created_by": self.created_by,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


class ManifestBuilder:
    """Create signed manifest files for S3 audit partitions."""

    def __init__(self, version: str = "1.0", created_by: str = "audit-manifest-builder") -> None:
        self.version = version
        self.created_by = created_by

    def build(self, partition: str, objects: Iterable[ManifestObject]) -> Manifest:
        items = list(objects)
        created_at = datetime.now(timezone.utc).isoformat()
        aggregate = self._aggregate_hash(items)
        return Manifest(
            version=self.version,
            created_at=created_at,
            partition=partition,
            objects=items,
            aggregate_sha256=aggregate,
            created_by=self.created_by,
        )

    def sign(self, manifest: Manifest, secret: bytes) -> str:
        payload = manifest.to_json().encode("utf-8")
        signature = hmac.new(secret, payload, sha256).digest()
        return base64.b64encode(signature).decode("ascii")

    @staticmethod
    def _aggregate_hash(objects: Iterable[ManifestObject]) -> str:
        digest = sha256()
        for obj in sorted(objects, key=lambda o: o.key):
            digest.update(obj.sha256.encode("utf-8"))
        return digest.hexdigest()
