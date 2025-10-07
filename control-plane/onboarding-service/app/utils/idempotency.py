# app/utils/idempotency.py
import hashlib, json, gzip
from datetime import datetime, timedelta, timezone

LOCK_SECONDS = 30
TTL_HOURS = 24

def canonical_body(body: bytes | None) -> bytes:
    if not body:
        return b""
    try:
        # JSON canonicalization (stable keys & whitespace)
        obj = json.loads(body.decode("utf-8"))
        return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    except Exception:
        return body  # non-JSON payloads

def fingerprint(method: str, path: str, body: bytes | None) -> str:
    canon = canonical_body(body)
    h = hashlib.sha256()
    h.update(method.upper().encode()); h.update(b"|")
    h.update(path.encode());           h.update(b"|")
    h.update(canon)
    return h.hexdigest()

def now_utc():
    return datetime.now(timezone.utc)

def lock_until():
    return now_utc() + timedelta(seconds=LOCK_SECONDS)

def ttl_expires():
    return now_utc() + timedelta(hours=TTL_HOURS)

def pack_body(data: dict | list | str | bytes) -> bytes:
    raw = data if isinstance(data, (bytes, bytearray)) else json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return gzip.compress(raw)

def unpack_body(blob: bytes | None):
    if not blob:
        return None
    raw = gzip.decompress(blob)
    try:
        return json.loads(raw)
    except Exception:
        return raw.decode("utf-8", errors="ignore")