import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.domain.models import Tenant, TenantStatus

def get_tenant(db: Session, tenant_id: uuid.UUID) -> Tenant | None:
    return db.get(Tenant, tenant_id)

def get_tenant_by_slug(db: Session, slug: str) -> Tenant | None:
    return db.execute(select(Tenant).where(Tenant.tenant_slug == slug)).scalar_one_or_none()

def create_or_get_tenant(db: Session, name: str, slug: str) -> Tenant:
    t = get_tenant_by_slug(db, slug)
    if t:
        return t
    t = Tenant(tenant_id=uuid.uuid4(), tenant_slug=slug, name=name, status=TenantStatus.pending_activation)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t