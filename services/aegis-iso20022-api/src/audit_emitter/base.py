from abc import ABC, abstractmethod

from audit_event import AuditEvent

class AuditEmitter(ABC):
    """Abstract emitter for audit events."""

    @abstractmethod
    def emit(self, event: AuditEvent) -> None:
        """Deliver an audit event to the downstream pipeline."""
