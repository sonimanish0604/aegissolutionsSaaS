from typing import Tuple, List
from .schema import AuditEvent, SENSITIVE_KEYS

def validate_event_dict(d: dict) -> Tuple[bool, List[str]]:
    errors = []
    try:
        evt = AuditEvent.model_validate(d)
    except Exception as ex:
        return False, [f"schema_error:{ex}"]

    # policy checks:
    if not evt.service: errors.append("service_required")
    if not evt.env: errors.append("env_required")
    if evt.method not in {"POST","PUT","PATCH","DELETE"}:
        errors.append("method_not_mutating")

    # ensure redaction: payload must not leak sensitive keys
    if isinstance(evt.payload, dict):
        lower_keys = {k.lower() for k in evt.payload.keys()}
        leaked = lower_keys & SENSITIVE_KEYS
        if leaked:
            errors.append(f"payload_leak:{','.join(sorted(leaked))}")

    return (len(errors) == 0), errors