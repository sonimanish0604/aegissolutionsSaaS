from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

CURRENT_DIR = Path(__file__).resolve().parent
SERVICE_ROOT = CURRENT_DIR.parent

if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))

from tests.category1_samples import SAMPLES
from src.translator_core.mt_parser import MTParser
from src.translator_core.mapping_store import MappingStore
from src.translator_core.transformer import Transformer
from src.translator_core.mx_builder import MXBuilder
from src.translator_core.xsd_validator import XSDValidator
from src.prevalidator_core import PrevalidationEngine


DEFAULT_PREFIX = "category1MXtransform"
REPORTS_DIR = Path("reports")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _sanitise_mt_type(mt_type: str) -> str:
    return mt_type.replace("-", "")


def _classify_mt195_variant(parsed_fields: dict) -> str | None:
    field72 = parsed_fields.get("72")
    if not field72:
        return None
    if isinstance(field72, list):
        text = "\n".join(field72)
    else:
        text = str(field72)
    text_normalized = text.upper().replace("-", " ")
    if "/QUERY/UNABLE TO APPLY" in text_normalized:
        return "unable_to_apply"
    if "/QUERY/CLAIM NON RECEIPT" in text_normalized:
        return "claim_non_receipt"
    if "/QUERY/REQUEST FOR DUPLICATE" in text_normalized:
        return "request_duplicate"
    return None


def _classify_mt196_variant(parsed_fields: dict) -> str | None:
    field76 = parsed_fields.get("76") if isinstance(parsed_fields, dict) else None
    if not field76:
        return None
    if isinstance(field76, list):
        text = "\n".join(field76).upper()
    else:
        text = str(field76).upper()
    keywords = ("CANCEL", "RJCR", "PDCR", "CNCL", "ACCR")
    return "cancellation" if any(key in text for key in keywords) else "information"


def _detect_variant(mt_type_key: str, parsed_fields: dict, sample_meta: dict[str, Any]) -> str | None:
    if "variant" in sample_meta:
        return sample_meta["variant"]
    if mt_type_key == "MT102STP":
        return "stp"
    if mt_type_key == "MT195":
        return _classify_mt195_variant(parsed_fields)
    if mt_type_key == "MT196":
        return _classify_mt196_variant(parsed_fields)
    return None


def _build_prevalidation_record(result: Any | None, enabled: bool) -> dict[str, Any]:
    if not enabled or result is None:
        return {
            "enabled": False,
            "valid": None,
            "errors": [],
            "warnings": [],
        }
    data = result.to_dict()
    data["enabled"] = True
    return data


def generate(prevalidate: bool = True) -> dict[str, Any]:
    ts = _now_iso()

    parser = MTParser()
    store = MappingStore()
    builder = MXBuilder()
    transformer = Transformer()
    prevalidator = PrevalidationEngine()

    samples_out: list[dict[str, Any]] = []

    for label, payload in SAMPLES.items():
        mt_raw = payload["mt_raw"]
        requested_type = payload.get("force_type") or label
        mt_key = _sanitise_mt_type(requested_type)

        parsed = parser.parse(mt_key, mt_raw)
        parsed_fields = parsed.get("fields", {})
        variant = _detect_variant(mt_key, parsed_fields, payload)

        if prevalidate:
            force_type = payload.get("force_type") or requested_type
            pre_validation = prevalidator.validate(mt_raw, force_type=force_type)
        else:
            pre_validation = None
        pre_validation_dict = _build_prevalidation_record(pre_validation, prevalidate)
        prevalidation_valid = (
            pre_validation_dict["valid"] if pre_validation_dict["enabled"] else True
        )

        mapping_rel, mx_type, xsd_dir = store.resolve(mt_key, variant=variant)
        if not mapping_rel or not mx_type or not xsd_dir:
            samples_out.append(
                {
                    "label": label,
                    "mt_type": requested_type,
                    "mx_type": None,
                    "variant": variant,
                    "status": "ok",
                    "code": "NO_CONVERSION_APPLICABLE",
                    "mode": "pass_through",
                    "payload_preserved": True,
                    "notes": f"{requested_type} carried unchanged. No ISO 20022 conversion performed.",
                    "xml": None,
                    "xsd_ok": None,
                    "xsd_errors": [],
                    "mapping": None,
                    "prevalidation": pre_validation_dict,
                }
            )
            continue

        mapping_path = (store.service_root / mapping_rel).resolve()
        xsd_path = Path(xsd_dir).resolve()

        if not mapping_path.exists() or not xsd_path.exists():
            samples_out.append(
                {
                    "label": label,
                    "mt_type": requested_type,
                    "mx_type": None,
                    "variant": variant,
                    "status": "error",
                    "code": "PROFILE_INCOMPLETE",
                    "mode": "pass_through",
                    "payload_preserved": True,
                    "notes": f"Mapping profile incomplete for {requested_type}.",
                    "xml": None,
                    "xsd_ok": None,
                    "xsd_errors": [],
                    "mapping": mapping_rel,
                    "prevalidation": pre_validation_dict,
                }
            )
            continue

        if not prevalidation_valid:
            error_notes = "; ".join(e["message"] for e in pre_validation_dict.get("errors", [])) or "Prevalidation failed"
            samples_out.append(
                {
                    "label": label,
                    "mt_type": requested_type,
                    "mx_type": None,
                    "variant": variant,
                    "status": "error",
                    "code": "PREVALIDATION_FAILED",
                    "mode": "pass_through",
                    "payload_preserved": True,
                    "notes": error_notes,
                    "xml": None,
                    "xsd_ok": None,
                    "xsd_errors": [],
                    "mapping": mapping_rel,
                    "prevalidation": pre_validation_dict,
                }
            )
            continue

        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))

        flat, audit_details = transformer.apply(mapping, parsed)
        xml_payload = builder.build(mx_type, flat)
        validator = XSDValidator(str(xsd_path), mx_type)
        ok, errors = validator.validate(xml_payload)

        samples_out.append(
                {
                    "label": label,
                    "mt_type": requested_type,
                    "mx_type": mx_type,
                    "variant": variant,
                    "status": "ok" if ok else "error",
                    "code": "CONVERTED" if ok else "XSD_INVALID",
                    "mode": "translate",
                    "payload_preserved": False,
                "notes": None if ok else "; ".join(errors),
                "xml": xml_payload,
                "xsd_ok": ok,
                "xsd_errors": errors,
                "mapping": mapping_rel,
                "mapped_count": len(audit_details["mapped"]),
                "prevalidation": pre_validation_dict,
            }
        )

    return {"generated_at": ts, "samples": samples_out}


def write_json(report: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def write_xml(report: dict[str, Any], path: Path) -> None:
    lines: list[str] = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append(f'<mxTransforms generatedAt="{report["generated_at"]}">')
    for sample in report["samples"]:
        prevalidation_info = sample.get("prevalidation", {})
        pre_attr = (
            "not_enabled"
            if not prevalidation_info.get("enabled")
            else ("ok" if prevalidation_info.get("valid") else "fail")
        )
        attrs = {
            "label": sample["label"],
            "mtType": sample["mt_type"],
            "preValidation": pre_attr,
            "mxType": sample["mx_type"] if sample["mx_type"] is not None else "None",
            "variant": sample["variant"] or "",
            "status": sample["status"],
            "code": sample["code"],
        }
        attr_str = " ".join(f'{k}="{html.escape(str(v), quote=True)}"' for k, v in attrs.items())
        lines.append(f"  <sample {attr_str}>")
        if sample["mode"] == "pass_through":
            note = html.escape(sample["notes"] or "")
            lines.append(f"    <notes>{note}</notes>")
        else:
            lines.append(f"    <mapping>{html.escape(sample['mapping'] or '')}</mapping>")
            xml_body = sample["xml"] or ""
            lines.append("    <payload><![CDATA[" + xml_body + "]]></payload>")
        lines.append("  </sample>")
    lines.append("</mxTransforms>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(report: dict[str, Any], path: Path) -> None:
    head = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Category 1 MT→MX Transform</title>
  <style>
    body {{ font-family: sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 0.5rem; vertical-align: top; }}
    th {{ background: #f0f0f0; }}
    textarea {{ width: 100%; font-family: monospace; }}
  </style>
</head>
<body>
  <h1>Category 1 MT→MX Transform Summary</h1>
  <p>Generated at {html.escape(report["generated_at"])}</p>
  <table>
    <thead>
      <tr>
        <th>Label</th>
        <th>MT Type</th>
        <th>MT Prevalidate</th>
        <th>MX Type</th>
        <th>Variant</th>
        <th>Mapping</th>
        <th>Status</th>
        <th>Details</th>
        <th>MX Payload</th>
      </tr>
    </thead>
    <tbody>
"""

    rows: list[str] = []
    for sample in report["samples"]:
        variant = sample["variant"] or "—"
        mapping = sample["mapping"] or ""
        status = "PASS-THROUGH" if sample["mode"] == "pass_through" else ("OK" if sample["status"] == "ok" else "XSD ERROR")
        details = sample["notes"] or "—"
        mx_type = sample["mx_type"] if sample["mx_type"] is not None else "None"
        payload = sample["xml"] or ""
        pre_info = sample.get("prevalidation", {})
        if not pre_info.get("enabled"):
            pre_status_text = "NOT ENABLED"
        else:
            pre_status_text = "OK" if pre_info.get("valid") else "FAIL"
        rows.append(
            "      <tr>"
            f"<td>{html.escape(sample['label'])}</td>"
            f"<td>{html.escape(sample['mt_type'])}</td>"
            f"<td>{html.escape(pre_status_text)}</td>"
            f"<td>{html.escape(mx_type)}</td>"
            f"<td>{html.escape(variant)}</td>"
            f"<td>{html.escape(mapping)}</td>"
            f"<td>{html.escape(status)}</td>"
            f"<td>{html.escape(details)}</td>"
            f"<td><textarea readonly rows=\"12\" cols=\"80\">{html.escape(payload)}</textarea></td>"
            "</tr>"
        )

    tail = """    </tbody>
  </table>
</body>
</html>
"""
    path.write_text(head + "\n".join(rows) + "\n" + tail, encoding="utf-8")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate Category 1 MT→MX transformation reports")
    parser.add_argument(
        "--skip-prevalidation",
        action="store_true",
        help="Skip MT prevalidation and mark status as NOT ENABLED",
    )
    parser.add_argument(
        "--output-prefix",
        default=DEFAULT_PREFIX,
        help="Base filename for generated reports (default: %(default)s)",
    )
    args = parser.parse_args()

    report = generate(prevalidate=not args.skip_prevalidation)

    prefix = args.output_prefix
    REPORTS_DIR.mkdir(exist_ok=True)
    json_path = REPORTS_DIR / f"{prefix}.json"
    xml_path = REPORTS_DIR / f"{prefix}.xml"
    html_path = REPORTS_DIR / f"{prefix}.html"

    write_json(report, json_path)
    write_xml(report, xml_path)
    write_html(report, html_path)


if __name__ == "__main__":
    main()
