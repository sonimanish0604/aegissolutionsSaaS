from __future__ import annotations
import os, json, asyncio
from typing import Mapping
from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
STREAM_KEY = os.getenv("AUDIT_STREAM_KEY", "audit:events")
STREAM_MAXLEN = int(os.getenv("AUDIT_STREAM_MAXLEN", "1000000"))  # soft trim

class AuditPublisher:
    def __init__(self, url: str = REDIS_URL, stream: str = STREAM_KEY):
        self._redis = Redis.from_url(url, decode_responses=True)
        self._stream = stream

    async def publish(self, event: Mapping) -> None:
        # XADD audit:events MAXLEN ~ N * fields...
        fields = {"json": json.dumps(event, separators=(",", ":"), ensure_ascii=False)}
        try:
            await self._redis.xadd(self._stream, fields, maxlen=STREAM_MAXLEN, approximate=True)
        except Exception:
            # swallow: auditing must not break API responses
            pass

    async def close(self):
        try: await self._redis.aclose()
        except Exception: pass

publisher_singleton = AuditPublisher()