import logging

from audit_event import AuditEvent
from .base import AuditEmitter

logger = logging.getLogger("audit")

class LoggingEmitter(AuditEmitter):
    """Simple emitter that logs audit events."""

    def emit(self, event: AuditEvent) -> None:
        logger.info("audit_event", extra={"audit": event.to_dict()})
