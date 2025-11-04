from contextvars import ContextVar
from typing import Any, Dict

_AUDIT_CONTEXT: ContextVar[Dict[str, Any]] = ContextVar("audit_context", default={})

def set_audit_context(data: Dict[str, Any]) -> None:
    _AUDIT_CONTEXT.set(data)

def get_audit_context() -> Dict[str, Any]:
    return _AUDIT_CONTEXT.get()
