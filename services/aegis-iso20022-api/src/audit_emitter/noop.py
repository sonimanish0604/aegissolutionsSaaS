from audit_event import AuditEvent
from .base import AuditEmitter

class NoopEmitter(AuditEmitter):
    """Emitter that drops audit events (useful for tests)."""

    def emit(self, event: AuditEvent) -> None:
        return
