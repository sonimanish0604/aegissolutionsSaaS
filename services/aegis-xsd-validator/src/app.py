from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

import xmlschema
import logging
app = FastAPI(title="Aegis XSD Validation Service")


def _read_upload(upload: Optional[UploadFile]) -> Optional[bytes]:
    if upload is None:
        return None
    content = upload.file.read()
    upload.file.close()
    return content


def _validate_xmlschema(xsd_bytes: bytes, xml_bytes: bytes) -> dict:
    schema = xmlschema.XMLSchema11(xsd_bytes)
    try:
        schema.validate(xml_bytes)
        return {"engine": "xmlschema", "ok": True, "errors": []}
    except xmlschema.XMLSchemaValidationError as exc:  # type: ignore[attr-defined]
        logging.warning("XML Schema validation failed: %s", exc)
        return {"engine": "xmlschema", "ok": False, "errors": ["XML schema validation failed"]}


def _validate_saxon_sim(xml_bytes: bytes) -> dict:
    """
    Lightweight simulator for Saxon-EE.

    This does not perform real validation; instead, it mimics success/failure
    conditions to exercise the remote backend wiring during development.
    """
    text = xml_bytes.decode("utf-8", errors="ignore")
    if "<INVALID" in text.upper():
        return {
            "engine": "saxon-sim",
            "ok": False,
            "errors": ["Simulated Saxon failure triggered by '<INVALID' marker."],
        }
    return {"engine": "saxon-sim", "ok": True, "errors": []}


@app.post("/validate")
async def validate(
    engine: str = Form(...),
    mx_type: str = Form(""),
    xsd: UploadFile | None = File(None),
    xml: UploadFile = File(...),
):
    xsd_bytes = _read_upload(xsd)
    xml_bytes = _read_upload(xml)
    if xml_bytes is None:
        raise HTTPException(status_code=400, detail="XML payload is required")

    engine_normalized = engine.lower()

    if engine_normalized in {"xmlschema", "xmlschema11"}:
        if xsd_bytes is None:
            raise HTTPException(status_code=400, detail="XSD file is required for xmlschema engine")
        result = _validate_xmlschema(xsd_bytes, xml_bytes)
        result["mx_type"] = mx_type
        return result

    if engine_normalized in {"saxon-sim", "saxon"}:
        result = _validate_saxon_sim(xml_bytes)
        result["mx_type"] = mx_type
        return result

    raise HTTPException(status_code=400, detail=f"Unsupported validation engine '{engine}'")
