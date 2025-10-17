# app/models/audit.py
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB, TIMESTAMP
from sqlalchemy import BigInteger, Integer, Text, Boolean
from app.domain.models import Base

def now_utc():
    return datetime.now(timezone.utc)

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # new columns used by the writer
    event_id: Mapped[str] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False)
    service: Mapped[str] = mapped_column(Text, nullable=False)
    env: Mapped[str] = mapped_column(Text, nullable=False)
    method: Mapped[str | None] = mapped_column(Text, nullable=True)

    occurred_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_utc)
    tenant_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True))
    actor_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True))
    actor_type: Mapped[str] = mapped_column(Text)  # 'user' | 'service'
    source_ip: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None] = mapped_column(Text)
    correlation_id: Mapped[str | None] = mapped_column(Text)
    idempotency_key: Mapped[str | None] = mapped_column(Text)
    route: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    target_type: Mapped[str | None] = mapped_column(Text)
    target_id: Mapped[str | None] = mapped_column(Text)
    status_code: Mapped[int] = mapped_column(Integer)
    severity: Mapped[str] = mapped_column(Text, default="info")
    payload_redacted: Mapped[dict | None] = mapped_column(JSONB)

    # processing state (lightweight ingest table flags)
    processed_redis: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processed_rds:   Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attempts:        Mapped[int]  = mapped_column(Integer, default=0, nullable=False)
    last_error:      Mapped[str | None] = mapped_column(Text, nullable=True)
    next_retry_at:   Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)