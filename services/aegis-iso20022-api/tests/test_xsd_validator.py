from __future__ import annotations

import os
from pathlib import Path

import pytest

from src.translator_core import xsd_validator
from src.translator_core.xsd_validator import XSDValidator, xmlschema  # type: ignore


def _write_sample_schema(directory: Path) -> None:
    schema = directory / "sample.xsd"
    schema.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="Document">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="Value" type="xs:string"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
""",
        encoding="utf-8",
    )


def test_lxml_backend_validates_success(tmp_path: Path):
    _write_sample_schema(tmp_path)
    validator = XSDValidator(str(tmp_path), "sample")
    ok, errors = validator.validate("<Document><Value>ok</Value></Document>")
    assert ok is True
    assert errors == []


def test_lxml_backend_flags_errors(tmp_path: Path):
    _write_sample_schema(tmp_path)
    validator = XSDValidator(str(tmp_path), "sample")
    ok, errors = validator.validate("<Document/>")
    assert ok is False
    assert errors


def test_validator_handles_missing_schema():
    validator = XSDValidator(None, "sample")
    ok, errors = validator.validate("<Document/>")
    assert ok is True
    assert any("skipped" in err.lower() for err in errors)


def test_request_xmlschema_without_dependency(monkeypatch):
    if xmlschema is not None:
        pytest.skip("xmlschema module available; dependency check not applicable")
    monkeypatch.setenv("XSD_VALIDATOR_BACKEND", "xmlschema11")
    with pytest.raises(RuntimeError):
        XSDValidator(None, "sample")
    monkeypatch.delenv("XSD_VALIDATOR_BACKEND", raising=False)


def test_remote_backend(monkeypatch, tmp_path: Path):
    if xsd_validator.httpx is None:
        pytest.skip("httpx not available")

    _write_sample_schema(tmp_path)

    class DummyResponse:
        def __init__(self, payload):
            self.status_code = 200
            self._payload = payload
            self.text = ""

        def json(self):
            return self._payload

    def fake_post(url, data=None, files=None, timeout=None):  # pylint: disable=unused-argument
        assert "engine" in data
        assert "mx_type" in data
        assert "xml" in files
        return DummyResponse({"ok": True, "errors": []})

    monkeypatch.setenv("XSD_VALIDATOR_BACKEND", "remote")
    monkeypatch.setenv("XSD_VALIDATOR_ENDPOINT", "http://validator.local/validate")
    monkeypatch.setattr(xsd_validator.httpx, "post", fake_post)

    try:
        validator = XSDValidator(str(tmp_path), "sample")
        ok, errors = validator.validate("<Document><Value>1</Value></Document>")
        assert ok is True
        assert errors == []
    finally:
        monkeypatch.delenv("XSD_VALIDATOR_BACKEND", raising=False)
        monkeypatch.delenv("XSD_VALIDATOR_ENDPOINT", raising=False)
