from __future__ import annotations

import hashlib
import json
from typing import Any


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_bytes(data: bytes) -> str:
    return f"sha256:{_digest(data)}"


def hash_text(text: str, *, encoding: str = "utf-8") -> str:
    return hash_bytes(text.encode(encoding))


def hash_json(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hash_bytes(payload)
