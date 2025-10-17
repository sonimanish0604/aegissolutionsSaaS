# app/services/audit.py
from __future__ import annotations
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, Optional
#from app.domain.models import AuditEvent  # your SQLAlchemy model mapped to audit_events
from app.models.audit import AuditEvent  # your SQLAlchemy model mapped to audit_events
from app.config import SERVICE_NAME, ENVIRONMENT

REDACT_KEYS = {"password", "secret", "token", "ssn", "dob", "email", "authorization"}

def _redact(obj: Any):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {k: ("***" if k.lower() in REDACT_KEYS else _redact(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact(x) for x in obj]
    return obj

async def write_audit_event(
    session: AsyncSession,
    *,
    route: str,
    method: str,
    status_code: int,
    action: str,
    tenant_id: Optional[str],
    actor_id: Optional[str],
    actor_type: str,
    source_ip: Optional[str],
    user_agent: Optional[str],
    correlation_id: Optional[str],
    idempotency_key: Optional[str],
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    severity: str = "info",
) -> str:
    evt = AuditEvent(
        event_id=str(uuid4()),
        service=SERVICE_NAME,
        env=ENVIRONMENT,
        route=route,
        method=method,
        action=action,
        status_code=status_code,
        tenant_id=tenant_id,
        actor_id=actor_id,
        actor_type=actor_type,
        source_ip=source_ip,
        user_agent=user_agent,
        correlation_id=correlation_id,
        idempotency_key=idempotency_key,
        target_type=target_type,
        target_id=target_id,
        severity=severity,
        payload_redacted=_redact(payload),
        processed_redis=False,
        processed_rds=False,
    )
    session.add(evt)
    await session.commit()
    return evt.event_id