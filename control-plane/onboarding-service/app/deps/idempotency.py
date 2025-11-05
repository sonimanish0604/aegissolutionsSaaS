# app/deps/idempotency.py
from fastapi import Header, HTTPException, Request, Response
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.models.idempotency import IdempotencyKey
from app.utils.idempotency import (
    fingerprint, now_utc, lock_until, ttl_expires, pack_body, unpack_body
)

IDEMPOTENCY_HEADER = "Idempotency-Key"

async def idempotency_guard(
    request: Request,
    session: AsyncSession,
    tenant_id: str | None,
    idempotency_key: str | None = Header(default=None, alias=IDEMPOTENCY_HEADER)
):
    if request.method not in ("POST", "PUT", "PATCH"):  # GET/DELETE usually skip
        return None

    if not idempotency_key:
        raise HTTPException(status_code=400, detail=f"{IDEMPOTENCY_HEADER} header is required")

    body = await request.body()
    fp = fingerprint(request.method, request.url.path, body)

    # Try fetch existing completed record
    q = select(IdempotencyKey).where(
        IdempotencyKey.idempotency_key == idempotency_key,
        IdempotencyKey.tenant_id == tenant_id
    )
    existing = (await session.execute(q)).scalar_one_or_none()
    if existing:
        # if in-progress lock and not expired => tell client to retry later
        if existing.status_code is None and existing.locked_until and existing.locked_until > now_utc():
            raise HTTPException(status_code=409, detail="Operation in progress. Retry later.")
        # completed => replay the cached response
        if existing.status_code is not None:
            return Response(
                content=(unpack_body(existing.response_body) if isinstance(unpack_body(existing.response_body), str) else
                         (existing.response_body or b"")).__str__().encode("utf-8"),
                status_code=existing.status_code,
                media_type="application/json"
            )

    # Create or lock record (upsert-ish)
    # We set a short lock window to prevent duplicate processing
    if not existing:
        stmt = insert(IdempotencyKey).values(
            idempotency_key=idempotency_key,
            tenant_id=tenant_id,
            request_fingerprint=fp,
            method=request.method,
            path=request.url.path,
            locked_until=lock_until(),
            ttl_expires_at=ttl_expires(),
        ).on_conflict_do_nothing(
            index_elements=["tenant_id", "idempotency_key"]
        )
        await session.execute(stmt)
        await session.commit()

    # Acquire lock if someone else inserted at the same time
    stmt = update(IdempotencyKey).where(
        IdempotencyKey.idempotency_key == idempotency_key,
        IdempotencyKey.tenant_id == tenant_id,
        (IdempotencyKey.locked_until.is_(None)) | (IdempotencyKey.locked_until < now_utc())
    ).values(locked_until=lock_until())
    res = await session.execute(stmt)
    await session.commit()

    if res.rowcount == 0:
        # Could not acquire lock -> another worker processing
        raise HTTPException(status_code=409, detail="Operation in progress. Retry later.")

    # return a small context object to set result later
    class IdempContext:
        def __init__(self, key): self.key = key
    return IdempContext(idempotency_key)