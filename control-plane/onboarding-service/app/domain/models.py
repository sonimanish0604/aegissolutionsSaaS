# app/models.py  (or wherever your models live)
from __future__ import annotations

from sqlalchemy import String, Text, JSON, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

import enum
import uuid
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass


def now() -> datetime:
    return datetime.now(timezone.utc)

class TenantStatus(str, enum.Enum):
    pending_activation = "pending_activation"
    active = "active"
    suspended = "suspended"
    canceled = "canceled"

class Tenant(Base):
    __tablename__ = "tenants"
    tenant_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    tenant_slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TenantStatus] = mapped_column(Enum(TenantStatus), default=TenantStatus.pending_activation)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=now)