"""Shim for kafka-python packaging quirks when vendor modules are missing."""

from __future__ import annotations

import selectors
import socket
import sys
import types

import six


def ensure_vendor_modules() -> None:
    """Provide kafka.vendor modules expected by kafka-python."""

    if "kafka.vendor.six" in sys.modules:
        return

    vendor_pkg = sys.modules.get("kafka.vendor")
    if vendor_pkg is None:
        vendor_pkg = types.ModuleType("kafka.vendor")
        vendor_pkg.__path__ = []  # type: ignore[attr-defined]
        sys.modules["kafka.vendor"] = vendor_pkg

    six_module = types.ModuleType("kafka.vendor.six")
    six_module.__dict__.update(six.__dict__)
    sys.modules["kafka.vendor.six"] = six_module
    sys.modules["kafka.vendor.six.moves"] = six.moves  # type: ignore[assignment]

    selectors_module = types.ModuleType("kafka.vendor.selectors34")
    selectors_module.__dict__.update(selectors.__dict__)
    sys.modules["kafka.vendor.selectors34"] = selectors_module

    socketpair_module = types.ModuleType("kafka.vendor.socketpair")
    socketpair_module.socketpair = getattr(socket, "socketpair", None)
    if socketpair_module.socketpair is None:
        def _fallback_socketpair():
            raise NotImplementedError("socketpair not available on this platform")

        socketpair_module.socketpair = _fallback_socketpair  # type: ignore[assignment]
    sys.modules["kafka.vendor.socketpair"] = socketpair_module
