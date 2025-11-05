# app/audit/adapters.py
from __future__ import annotations
import os
from typing import Protocol, Mapping, Any

# Reuse your existing publisher to avoid duplicate Redis handling
from app.audit.publisher import publisher_singleton

class CacheStream(Protocol):
    async def publish(self, event: Mapping[str, Any]) -> None: ...

class _LocalCacheStream:
    async def publish(self, event: Mapping[str, Any]) -> None:
        await publisher_singleton.publish(event)

def get_cache_stream() -> CacheStream:
    """Select cache stream by CLOUD_VENDOR; Local uses existing Redis publisher."""
    vendor = (os.getenv("CLOUD_VENDOR") or "local").lower()
    # For now, all vendors resolve to the same local Redis publisher until adapters are added.
    # Later:
    # if vendor == "aws": return AwsCacheStream(...)
    # elif vendor == "azure": return AzureCacheStream(...)
    # elif vendor == "gcp": return GcpCacheStream(...)
    # elif vendor == "render": return RenderCacheStream(...)
    return _LocalCacheStream()