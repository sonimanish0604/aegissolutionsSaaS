from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from ..translator_core.detector import Detector
from ..translator_core.mt_parser import MTParser
from ..translator_core.mapping_store import MappingStore
from ..translator_core.transformer import Transformer
from ..translator_core.mx_builder import MXBuilder
from ..translator_core.xsd_validator import XSDValidator
from ..translator_core.audit import AuditRecord, new_correlation_id
from ..translator_core.metrics import timer
from ..prevalidator_api.routes import router as prevalidator_router

app = FastAPI(title="Aegis ISO20022 Translator")
app.include_router(prevalidator_router)


@app.get("/")
def healthcheck():
    return {"status": "ok"}

class TranslateRequest(BaseModel):
    mt_raw: str
    force_type: str | None = None


def _classify_mt195_variant(parsed_fields: dict[str, list[str]] | dict) -> str | None:
    field72 = parsed_fields.get("72") if isinstance(parsed_fields, dict) else None
    if not field72:
        return None
    if isinstance(field72, list):
        text = "\n".join(field72).upper()
    else:
        text = str(field72).upper()
    text_normalized = text.replace("-", " ")
    if "/QUERY/UNABLE TO APPLY" in text_normalized:
        return "unable_to_apply"
    if "/QUERY/CLAIM NON RECEIPT" in text_normalized:
        return "claim_non_receipt"
    if "/QUERY/REQUEST FOR DUPLICATE" in text_normalized:
        return "request_duplicate"
    return None


def _classify_mt196_variant(parsed_fields: dict[str, list[str]] | dict) -> str | None:
    field76 = parsed_fields.get("76") if isinstance(parsed_fields, dict) else None
    if not field76:
        return None
    if isinstance(field76, list):
        text = "\n".join(field76).upper()
    else:
        text = str(field76).upper()
    keywords = ("CANCEL", "RJCR", "PDCR", "CNCL", "ACCR")
    return "cancellation" if any(key in text for key in keywords) else "information"


def _classify_mt102_variant(parsed: dict) -> str | None:
    block3 = None
    if isinstance(parsed, dict):
        block3 = parsed.get("blocks", {}).get("3")
    if not block3:
        return None
    if "119:STP" in str(block3).upper():
        return "stp"
    return None

@app.post("/translate")
def translate(req: TranslateRequest):
    corr = new_correlation_id(req.mt_raw[:5000])
    with timer() as elapsed:
        det = Detector()
        mt_type = req.force_type or det.detect(req.mt_raw)
        if not mt_type:
            raise HTTPException(400, "Could not detect MT type")

        parser = MTParser()
        parsed = parser.parse(mt_type, req.mt_raw)

        store = MappingStore()

        variant = None
        if mt_type == "MT195":
            fields = parsed.get("fields", {}) if isinstance(parsed, dict) else {}
            variant = _classify_mt195_variant(fields)
        elif mt_type == "MT196":
            fields = parsed.get("fields", {}) if isinstance(parsed, dict) else {}
            variant = _classify_mt196_variant(fields)
        elif mt_type == "MT102":
            variant = _classify_mt102_variant(parsed)

        def _pass_through():
            return {
                "status": "ok",
                "code": "NO_CONVERSION_APPLICABLE",
                "mt_type": mt_type.replace("MT", "", 1),
                "mode": "pass_through",
                "payload_preserved": True,
                "notes": f"{mt_type} carried unchanged. No ISO 20022 conversion performed.",
                "mt_raw": req.mt_raw,
            }

        try:
            mapping, mx_type, xsd_dir = store.load_profile(mt_type, variant=variant)
        except FileNotFoundError:
            return _pass_through()

        if not mapping or not mx_type or not xsd_dir:
            return _pass_through()
        if not Path(xsd_dir).exists():
            return _pass_through()

        # optional guard: lightweight XSD index (reuse your iso-bootstrap xsd_index.py if desired)
        transformer = Transformer(xsd_index=None)
        flat, audit_details = transformer.apply(mapping, parsed)

        xml = MXBuilder().build(mx_type, flat)
        ok, errors = XSDValidator(xsd_dir,mx_type).validate(xml)

        mp_info = store.resolve(mt_type, variant)
        if not mp_info[0]:
            mp_info = store.resolve(mt_type)
        mapping_profile = mp_info[0] or "unknown"

        record = AuditRecord(
            correlation_id=corr,
            source_mt=mt_type,
            target_mx=mx_type,
            mapping_profile=str(mapping_profile),
            xsd_version=mx_type,
            mapped_count=len(audit_details["mapped"]),
            error_count=len(audit_details["errors"]) + (0 if ok else len(errors)),
            validation_ok=ok,
            latency_ms=elapsed(),
            details={"transform": audit_details, "xsd_errors": errors},
        )

        return {
            "mx_type": mx_type,
            "xml": xml,
            "validation": {"ok": ok, "errors": errors},
            "metrics": {"latency_ms": record.latency_ms},
            "audit": record.__dict__,
        }
