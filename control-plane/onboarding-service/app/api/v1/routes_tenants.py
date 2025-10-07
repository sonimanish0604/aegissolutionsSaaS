import re, uuid
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.infra.db import get_db
from app.api.v1.schemas import CreateTenantRequest, TenantResponse
from app.infra.repositories import create_or_get_tenant, get_tenant

router = APIRouter()

def to_slug(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return s[:48]

@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(req: CreateTenantRequest, db: Session = Depends(get_db), idempotency_key: str | None = Header(default=None, convert_underscores=False)):
    # NOTE: idempotency store can be added later (persist key->response)
    slug = to_slug(req.name)
    t = create_or_get_tenant(db, name=req.name, slug=slug)
    # Return 200 if tenant already existed (simple idempotency semantics)
    code = status.HTTP_200_OK if t else status.HTTP_201_CREATED
    return TenantResponse(
        tenant_id=str(t.tenant_id),
        tenant_slug=t.tenant_slug,
        status=t.status.value,
        plan=req.plan,
        products=[{"code": c, "plan": req.plan or "free", "status": "active"} for c in (req.product_codes or [])],
    )

@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
def read_tenant(tenant_id: str, db: Session = Depends(get_db)):
    try:
        tid = uuid.UUID(tenant_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid tenant_id")
    t = get_tenant(db, tid)
    if not t:
        raise HTTPException(status_code=404, detail="tenant not found")
    return TenantResponse(
        tenant_id=str(t.tenant_id),
        tenant_slug=t.tenant_slug,
        status=t.status.value,
        plan=None,
        products=[]
    )