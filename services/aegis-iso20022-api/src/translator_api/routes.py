from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from enum import Enum
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel
from pathlib import Path
import io
import json
import zipfile
import logging
import os
from ..translator_core.detector import Detector
from ..translator_core.mt_parser import MTParser
from ..translator_core.mapping_store import MappingStore
from ..translator_core.transformer import Transformer
from ..translator_core.mx_builder import MXBuilder
from ..translator_core.xsd_validator import XSDValidator
from ..translator_core.audit import AuditRecord, new_correlation_id
from ..translator_core.metrics import timer
from ..prevalidator_api.routes import router as prevalidator_router
from ..prevalidator_core import PrevalidationEngine
from .batch import BatchFile, BatchParseError, parse_batch_payload
from audit_middleware import AuditMiddleware
from audit_emitter import KafkaAuditEmitter, LoggingEmitter

app = FastAPI(title="Aegis ISO20022 Translator")
app.include_router(prevalidator_router)
logger = logging.getLogger(__name__)

prevalidation_engine = PrevalidationEngine()
_audit_emitter = None


def _init_audit_emitter():
    global _audit_emitter
    if _audit_emitter is not None:
        return _audit_emitter
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    topic = os.getenv("AUDIT_TOPIC", "audit.events")
    emitter = None
    if bootstrap and KafkaAuditEmitter:
        try:
            emitter = KafkaAuditEmitter(bootstrap_servers=bootstrap, topic=topic)
            logger.info("Audit emitter configured for Kafka topic %s", topic)
        except Exception as exc:  # pragma: no cover - fallback path
            logger.warning("Falling back to logging audit emitter: %s", exc)
            emitter = None
    if emitter is None:
        emitter = LoggingEmitter()
    _audit_emitter = emitter
    return emitter


app.add_middleware(AuditMiddleware, emitter=_init_audit_emitter())


@app.on_event("shutdown")
async def shutdown_audit_emitter():
    emitter = _init_audit_emitter()
    close = getattr(emitter, "close", None)
    if callable(close):  # pragma: no cover - clean shutdown
        close()


@app.get("/")
def healthcheck():
    return {"status": "ok"}


class TranslateRequest(BaseModel):
    mt_raw: str
    force_type: str | None = None
    prevalidate: bool = True


class BatchResponseFormat(str, Enum):
    zip = "zip"
    json = "json"


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

        if req.prevalidate:
            pre_result = prevalidation_engine.validate(req.mt_raw, force_type=req.force_type or mt_type)
            if not pre_result.valid:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "message": "Prevalidation failed",
                        "result": pre_result.to_dict(),
                    },
                )

        def _pass_through():
            elapsed_ms = elapsed()
            return {
                "status": "ok",
                "code": "NO_CONVERSION_APPLICABLE",
                "mt_type": mt_type.replace("MT", "", 1),
                "mx_type": None,
                "mode": "pass_through",
                "payload_preserved": True,
                "notes": f"{mt_type} carried unchanged. No ISO 20022 conversion performed.",
                "mt_raw": req.mt_raw,
                "validation": {"ok": True, "errors": []},
                "metrics": {"latency_ms": elapsed_ms},
            }

        try:
            mapping, mx_type, xsd_dir = store.load_profile(mt_type, variant=variant)
        except FileNotFoundError:
            return _pass_through()

        if not mapping or not mx_type:
            return _pass_through()

        # optional guard: lightweight XSD index (reuse your iso-bootstrap xsd_index.py if desired)
        transformer = Transformer(xsd_index=None)
        flat, audit_details = transformer.apply(mapping, parsed)

        xml = MXBuilder().build(mx_type, flat)
        validator = XSDValidator(xsd_dir, mx_type)
        ok, errors = validator.validate(xml)
        validator_engine = validator.engine_name()

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
            details={
                "transform": audit_details,
                "xsd_errors": errors,
            },
            xml_validator=validator_engine,
        )

        return {
            "mx_type": mx_type,
            "xml": xml,
            "validation": {"ok": ok, "errors": errors},
            "metrics": {"latency_ms": record.latency_ms},
            "audit": record.__dict__,
        }


def _process_message(mt_raw: str, prevalidate: bool) -> dict:
    request = TranslateRequest(mt_raw=mt_raw, prevalidate=prevalidate)
    return translate(request)


def _summarize_batch(batch: BatchFile, results: list[dict]) -> dict:
    succeeded = sum(1 for r in results if r["status"] == "ok")
    failed = len(results) - succeeded
    return {
        "source": batch.source_name,
        "header": batch.header,
        "trailer": batch.trailer,
        "summary": {
            "total": len(batch.messages),
            "succeeded": succeeded,
            "failed": failed,
        },
        "results": results,
    }


@app.post("/translate/batch")
async def translate_batch(
    file: UploadFile = File(...),
    prevalidate: bool = True,
    max_workers: int = 4,
    responseFileFormat: BatchResponseFormat = BatchResponseFormat.zip,
):
    if max_workers < 1:
        raise HTTPException(status_code=400, detail="max_workers must be at least 1")

    payload = await file.read()
    try:
        batches = parse_batch_payload(file.filename or "batch.dat", payload)
    except BatchParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    aggregate_results: list[dict] = []
    total_messages = 0
    total_success = 0
    total_failed = 0

    for batch in batches:
        workers = min(max_workers, len(batch.messages))
        if workers < 1:
            workers = 1
        jobs = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for message in batch.messages:
                future = executor.submit(_process_message, message.mt_raw, prevalidate)
                jobs.append((message, future))

        batch_results: list[dict] = []
        for message, future in jobs:
            try:
                result = future.result()
                audit = result.get("audit", {}) or {}
                validator_engine = audit.get("xml_validator")
                batch_results.append(
                    {
                        "index": message.index,
                        "status": "ok",
                        "mt_type": result.get("audit", {}).get("source_mt") or result.get("mt_type"),
                        "mx_type": result.get("mx_type"),
                        "validation": result.get("validation"),
                        "xml": result.get("xml"),
                        "metrics": result.get("metrics"),
                        "audit": result.get("audit"),
                        "xml_validator": validator_engine,
                    }
                )
            except HTTPException as exc:
                batch_results.append(
                    {
                        "index": message.index,
                        "status": "error",
                        "error": {
                            "status_code": exc.status_code,
                            "detail": exc.detail,
                        },
                    }
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception("Exception occurred while processing message index %s in batch %s", message.index, batch.source_name)
                batch_results.append(
                    {
                        "index": message.index,
                        "status": "error",
                        "error": {
                            "status_code": 500,
                            "detail": "Internal server error",
                        },
                    }
                )

        batch_results.sort(key=lambda item: item["index"])
        summary = _summarize_batch(batch, batch_results)
        aggregate_results.append(summary)

        total_messages += summary["summary"]["total"]
        total_success += summary["summary"]["succeeded"]
        total_failed += summary["summary"]["failed"]

    processed_at = datetime.now(timezone.utc)
    processed_at_iso = processed_at.isoformat()
    summary = {
        "batches": aggregate_results,
        "summary": {
            "total_batches": len(aggregate_results),
            "total_messages": total_messages,
            "succeeded": total_success,
            "failed": total_failed,
            "processed_at": processed_at_iso,
        },
    }

    fmt = responseFileFormat.value

    if fmt == "json":
        return summary

    archive = io.BytesIO()
    with zipfile.ZipFile(archive, mode="w") as zf:
        zip_meta = summary.copy()
        zip_meta["generated_at"] = processed_at_iso
        zf.writestr("summary.json", json.dumps(zip_meta, indent=2))
        for batch in aggregate_results:
            batch_id = batch["source"]
            for result in batch["results"]:
                idx = result["index"]
                prefix = f"{batch_id}/record-{idx:03d}"
                if result["status"] == "ok" and result.get("xml"):
                    mx_type = result.get("mx_type") or "mx"
                    zf.writestr(f"{prefix}_{mx_type}.xml", result["xml"])
                else:
                    zf.writestr(f"{prefix}_error.json", json.dumps(result, indent=2))

    archive.seek(0)
    filename = f"translate-batch-{aggregate_results[0]['source'] if aggregate_results else 'results'}.zip"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    return Response(
        content=archive.getvalue(),
        media_type="application/zip",
        headers=headers,
    )
