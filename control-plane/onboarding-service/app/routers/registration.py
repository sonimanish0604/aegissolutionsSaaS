# app/routers/registration.py
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.db_async import get_async_session
from app.deps.idempotency import idempotency_guard
from app.services.idempotency_committer import commit_idempotent_result

# optional context + audit (uncomment if those files exist)
from app.deps.context import get_request_context, RequestContext  # make sure this file exists
from app.services.audit import audit_log                           # make sure this file exists

# if you have a tenancy dep, import it; else set tenant_id=None below
# from app.deps.tenancy import get_tenant_id

router = APIRouter(prefix="/registrations", tags=["registrations"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_registration(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    # tenant_id: str | None = Depends(get_tenant_id),  # uncomment when available
    ctx: RequestContext = Depends(get_request_context),  # remove if you don't want context yet
    idemp_ctx = Depends(idempotency_guard),
) -> dict:
    # ---- your business logic
    payload = {"registration_id": "abc123", "status": "pending"}
    status_code = status.HTTP_201_CREATED

    # idempotency: save canonical result
    if idemp_ctx:
        await commit_idempotent_result(session, idemp_ctx.key, None, status_code, payload)  # replace None with tenant_id

    # audit (do not fail the main request if audit fails)
    try:
        await audit_log(
            session,
            tenant_id=None,  # replace with tenant_id when you wire it
            actor_id=None,
            actor_type="service",
            source_ip=ctx.source_ip,
            user_agent=ctx.user_agent,
            correlation_id=ctx.correlation_id,
            idempotency_key=ctx.idempotency_key,
            route=ctx.route,
            action="registration.create",
            status_code=status_code,
            target_type="registration",
            target_id=payload["registration_id"],
            payload=payload,
            severity="info",
        )
    except Exception:
        pass

    return payload