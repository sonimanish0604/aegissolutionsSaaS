# app/routers/registration.py
from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.deps.tenancy import get_tenant_id  # your existing dependency
from app.deps.idempotency import idempotency_guard
from app.services.idempotency_committer import commit_idempotent_result

router = APIRouter(prefix="/registrations", tags=["registrations"])

@router.post("", status_code=201)
async def create_registration(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    tenant_id: str | None = Depends(get_tenant_id),
    idemp_ctx = Depends(idempotency_guard)
):
    # If idempotency_guard returned a Response, FastAPI would have short-circuited.
    # Here we actually perform the work exactly once.
    # ... your business logic ...
    # example result:
    payload = {"registration_id": "abc123", "status": "pending"}
    status_code = 201

    # Save the result so future replays return the same
    if idemp_ctx:
        await commit_idempotent_result(session, idemp_ctx.key, tenant_id, status_code, payload)

    return payload