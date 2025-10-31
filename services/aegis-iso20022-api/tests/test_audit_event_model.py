from __future__ import annotations

import sys
from pathlib import Path

CURRENT = Path(__file__).resolve().parent
SRC = CURRENT.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from uuid import uuid4

from audit_utils import AuditEvent, hash_text  # noqa: E402  pylint: disable=wrong-import-position


def test_audit_event_defaults():
    event = AuditEvent()
    payload = event.to_dict()
    assert payload["v"] == "1.0"
    assert payload["hash"] == {}
    assert payload["tenant_uuid"] == ""


def test_audit_event_hash_helpers():
    event = AuditEvent(ts="2025-10-30T00:00:00Z", tenant_uuid=str(uuid4()))
    event.with_hash("mt", "{1:F01...}")
    assert "mt" in event.hash
    assert event.hash["mt"].startswith("sha256:")

    digest = hash_text("sample")
    assert digest.startswith("sha256:")
