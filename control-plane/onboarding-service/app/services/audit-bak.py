# app/services/audit.py
from app.models.audit import AuditEvent
from sqlalchemy.ext.asyncio import AsyncSession

REDACT_KEYS = {"password","secret","token","ssn","dob","email"}  # tailor as needed

def _redact(obj):
    if obj is None: return None
    if isinstance(obj, dict):
        return {k: ("***" if k.lower() in REDACT_KEYS else _redact(v)) for k,v in obj.items()}
    if isinstance(obj, list): return [_redact(x) for x in obj]
    return obj

async def audit_log(
    session: AsyncSession,
    *,
    tenant_id: str | None,
    actor_id: str | None,
    actor_type: str,
    source_ip: str | None,
    user_agent: str | None,
    correlation_id: str | None,
    idempotency_key: str | None,
    route: str,
    action: str,
    status_code: int,
    target_type: str | None = None,
    target_id: str | None = None,
    payload: dict | None = None,
    severity: str = "info"
):
    evt = AuditEvent(
        tenant_id=tenant_id,
        actor_id=actor_id,
        actor_type=actor_type,
        source_ip=source_ip,
        user_agent=user_agent,
        correlation_id=correlation_id,
        idempotency_key=idempotency_key,
        route=route,
        action=action,
        target_type=target_type,
        target_id=target_id,
        status_code=status_code,
        severity=severity,
        payload_redacted=_redact(payload),
    )
    session.add(evt)
    await session.commit()