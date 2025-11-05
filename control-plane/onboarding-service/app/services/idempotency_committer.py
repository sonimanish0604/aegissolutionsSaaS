# app/services/idempotency_committer.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.models.idempotency import IdempotencyKey
from app.utils.idempotency import pack_body, now_utc

async def commit_idempotent_result(
    session: AsyncSession,
    idempotency_key: str,
    tenant_id: str | None,
    status_code: int,
    response_payload
):
    stmt = update(IdempotencyKey).where(
        IdempotencyKey.idempotency_key == idempotency_key,
        IdempotencyKey.tenant_id == tenant_id
    ).values(
        status_code=status_code,
        response_body=pack_body(response_payload),
        locked_until=None,   # release lock
        updated_at=now_utc()
    )
    await session.execute(stmt)
    await session.commit()