from dataclasses import dataclass
from fastapi import Request

CORRELATION_HEADER = "x-correlation-id"
IDEMPOTENCY_HEADER = "idempotency-key"

@dataclass
class RequestContext:
    source_ip: str | None
    user_agent: str | None
    correlation_id: str | None
    idempotency_key: str | None
    route: str

def get_request_context(request: Request) -> RequestContext:
    src_ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    corr = request.headers.get(CORRELATION_HEADER)
    idemp = request.headers.get(IDEMPOTENCY_HEADER)
    route = f"{request.method} {request.url.path}"
    return RequestContext(
        source_ip=src_ip,
        user_agent=ua,
        correlation_id=corr,
        idempotency_key=idemp,
        route=route,
    )