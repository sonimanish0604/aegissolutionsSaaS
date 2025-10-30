from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from lxml import etree

try:
    import xmlschema  # type: ignore
except ImportError:  # pragma: no cover
    xmlschema = None  # type: ignore

try:
    import httpx  # type: ignore
except ImportError:  # pragma: no cover
    httpx = None  # type: ignore


@dataclass
class ValidationResult:
    """Container for schema validation outcome."""

    ok: bool
    errors: List[str]


class SchemaBackend(ABC):
    """Strategy interface for pluggable schema validation backends."""

    name: str = "base"

    def identifier(self) -> str:
        """Return a short identifier for audit logging."""
        return self.name

    @abstractmethod
    def load(self, schema_path: Optional[Path], mx_type: str) -> None:
        """Load/precompile the schema for the provided MX type."""

    @abstractmethod
    def validate(self, xml_str: str) -> ValidationResult:
        """Validate an XML payload and return the outcome."""


def _resolve_schema_path(xsd_dir: Optional[str], mx_type: str) -> Optional[Path]:
    """Locate the schema file for the given MX type or return None if absent."""
    if not xsd_dir:
        return None
    p = Path(xsd_dir)
    if p.is_file():
        return p
    if not p.exists():
        return None

    # Prefer an exact filename match (e.g. pacs.008.001.13.xsd).
    target = p / f"{mx_type}.xsd"
    if target.exists():
        return target

    # Fallback: search by targetNamespace.
    ns_wanted = f"urn:iso:std:iso:20022:tech:xsd:{mx_type}"
    for candidate in p.glob("*.xsd"):
        try:
            doc = etree.parse(str(candidate))
        except etree.XMLSyntaxError:
            continue
        root = doc.getroot()
        if root.get("targetNamespace") == ns_wanted:
            return candidate
    return None


class LxmlBackend(SchemaBackend):
    """XML Schema 1.0 validation backed by libxml2/lxml."""

    name = "lxml"

    def identifier(self) -> str:
        return "lxml"

    def __init__(self) -> None:
        self.schema = None
        self.schema_error: Optional[str] = None

    def load(self, schema_path: Optional[Path], mx_type: str) -> None:
        if not schema_path:
            self.schema = None
            self.schema_error = f"XSD file for {mx_type} not found"
            return

        try:
            doc = etree.parse(str(schema_path))
            self.schema = etree.XMLSchema(doc)
            self.schema_error = None
        except (etree.XMLSchemaParseError, etree.XMLSyntaxError) as exc:
            self.schema = None
            self.schema_error = f"lxml backend failed to parse schema: {exc}"

    def validate(self, xml_str: str) -> ValidationResult:
        doc = etree.fromstring(xml_str.encode("utf-8"))
        if self.schema is None:
            return ValidationResult(ok=True, errors=[self.schema_error or "XSD validation skipped (schema unavailable)"])
        ok = self.schema.validate(doc)
        return ValidationResult(ok=ok, errors=[str(e) for e in self.schema.error_log])


class XmlSchema11Backend(SchemaBackend):
    """XML Schema 1.1 validation using the python-xmlschema package."""

    name = "xmlschema11"

    def identifier(self) -> str:
        return "xmlschema11"

    def __init__(self) -> None:
        if xmlschema is None:
            raise RuntimeError("xmlschema package is not installed")
        self.schema = None
        self.schema_error: Optional[str] = None

    def load(self, schema_path: Optional[Path], mx_type: str) -> None:
        if schema_path is None:
            self.schema = None
            self.schema_error = f"XSD file for {mx_type} not found"
            return
        try:
            self.schema = xmlschema.XMLSchema11(str(schema_path))
            self.schema_error = None
        except xmlschema.XMLSchemaException as exc:  # type: ignore[attr-defined]
            self.schema = None
            self.schema_error = f"xmlschema backend failed to parse schema: {exc}"

    def validate(self, xml_str: str) -> ValidationResult:
        if self.schema is None:
            return ValidationResult(ok=True, errors=[self.schema_error or "XSD validation skipped (schema unavailable)"])
        try:
            self.schema.validate(xml_str)
            return ValidationResult(ok=True, errors=[])
        except xmlschema.XMLSchemaValidationError as exc:  # type: ignore[attr-defined]
            return ValidationResult(ok=False, errors=[str(exc)])


class RemoteBackend(SchemaBackend):
    """
    Delegates validation to an external HTTP service.

    Expected API contract:

        POST <endpoint>
          form-data:
            engine=<engine>
            mx_type=<mx type>
            xsd=<optional multipart file>
            xml=<multipart file with payload>

        Response 200 JSON: {"ok": bool, "errors": [str, ...]}
    """

    name = "remote"

    def identifier(self) -> str:
        return f"remote:{self.engine}"

    def __init__(self, mx_type: str) -> None:
        if httpx is None:
            raise RuntimeError("httpx is required for remote XSD validation backend")
        endpoint = os.getenv("XSD_VALIDATOR_ENDPOINT")
        if not endpoint:
            raise RuntimeError("XSD_VALIDATOR_ENDPOINT must be set for remote XSD validation backend")
        self.endpoint = endpoint
        self.engine = os.getenv("XSD_VALIDATOR_ENGINE", "xmlschema")
        self.mx_type = mx_type
        self.schema_payload: Optional[Tuple[str, bytes]] = None

    def load(self, schema_path: Optional[Path], mx_type: str) -> None:
        self.mx_type = mx_type
        if schema_path and schema_path.exists():
            self.schema_payload = (schema_path.name, schema_path.read_bytes())
        else:
            self.schema_payload = None

    def validate(self, xml_str: str) -> ValidationResult:
        files = {
            "xml": ("payload.xml", xml_str.encode("utf-8"), "application/xml"),
        }
        if self.schema_payload:
            files["xsd"] = (self.schema_payload[0], self.schema_payload[1], "application/xml")
        data = {
            "engine": self.engine,
            "mx_type": self.mx_type,
        }
        try:
            response = httpx.post(self.endpoint, data=data, files=files, timeout=30.0)  # type: ignore[arg-type]
        except Exception as exc:  # pragma: no cover - runtime failure paths
            return ValidationResult(ok=True, errors=[f"Remote XSD validation failed: {exc}"])

        if response.status_code >= 400:
            return ValidationResult(ok=True, errors=[f"Remote XSD validation HTTP {response.status_code}: {response.text}"])
        try:
            payload = response.json()
        except ValueError:
            return ValidationResult(ok=True, errors=[f"Remote XSD validation returned non-JSON payload: {response.text}"])

        ok = bool(payload.get("ok", False))
        errors = payload.get("errors", [])
        if not isinstance(errors, list):
            errors = [str(errors)]
        return ValidationResult(ok=ok, errors=[str(e) for e in errors])


def _select_backend(name: str, mx_type: str) -> SchemaBackend:
    """Instantiate the requested backend, falling back when appropriate."""
    normalized = name.lower()
    if normalized in {"auto", "xmlschema11"}:
        if xmlschema is not None:
            try:
                return XmlSchema11Backend()
            except RuntimeError:
                if normalized != "auto":
                    raise
        elif normalized == "xmlschema11":
            raise RuntimeError("xmlschema package is required for XML Schema 1.1 validation")
    if normalized in {"auto", "lxml"}:
        return LxmlBackend()
    if normalized in {"remote", "http"}:
        return RemoteBackend(mx_type=mx_type)
    raise ValueError(f"Unknown XSD validator backend '{name}'")


class XSDValidator:
    """Facade that validates XML documents using the configured backend."""

    def __init__(self, xsd_dir: Optional[str], mx_type: str):
        backend_name = os.getenv("XSD_VALIDATOR_BACKEND", "auto")
        backend = _select_backend(backend_name, mx_type)
        self.backend = backend
        schema_path = _resolve_schema_path(xsd_dir, mx_type)
        self.backend.load(schema_path, mx_type)

    def validate(self, xml_str: str) -> Tuple[bool, List[str]]:
        result = self.backend.validate(xml_str)
        return result.ok, result.errors

    def engine_name(self) -> str:
        return self.backend.identifier()
