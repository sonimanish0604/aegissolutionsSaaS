#!/usr/bin/env python3
"""Generate the monthly audit integrity report by injecting placeholder values."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict

REPORT_TEMPLATE = Path(__file__).resolve().parents[3] / 'docs' / 'audit_log_integrity_report.md'
DEFAULT_OUTPUT = Path.cwd() / "audit_log_integrity_report_rendered.md"


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def render_report(placeholders: Dict[str, str], output_path: Path) -> None:
    template = REPORT_TEMPLATE.read_text(encoding="utf-8")
    for key, value in placeholders.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    output_path.write_text(template, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render audit log integrity report")
    parser.add_argument("--period-start", help="ISO date for reporting period start", required=True)
    parser.add_argument("--period-end", help="ISO date for reporting period end", required=True)
    parser.add_argument("--environment", default="Production")
    parser.add_argument("--placeholders-json", type=Path, help="Optional JSON with extra placeholder values")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    placeholders = {
        "REPORT_DATE": dt.datetime.utcnow().strftime("%Y-%m-%d"),
        "PERIOD_START": args.period_start,
        "PERIOD_END": args.period_end,
        "ENVIRONMENT": args.environment,
        "VERIFICATION_TABLE": "_No data supplied_",
        "VERIFICATION_SUMMARY": "Verification job not run",
        "OBJECT_LOCK_MODE": "Compliance",
        "RETENTION_PERIOD": "2555",  # 7 years
        "LIFECYCLE_RULE": "Move to Glacier Deep Archive after 365 days",
        "KMS_ROTATION_STATUS": "Enabled",
        "SIGNER_ROLE_ARN": "arn:aws:iam::123456789012:role/audit-manifest-signer",
        "SIEM_FORWARDER_STATUS": "Active",
        "POLICY_REVIEW_DATE": args.period_end,
        "TOTAL_VERIFIED": "0",
        "FAILED_VERIFICATIONS": "0",
        "MISSING_OBJECTS": "0",
        "AVG_VERIFY_TIME": "N/A",
        "CLOUDTRAIL_RETENTION": "365",
        "EXCEPTION_TABLE": "_None recorded_",
        "REVIEW_DATE": args.period_end,
        "FINDINGS_SUMMARY": "No exceptions noted",
    }

    if args.placeholders_json:
        placeholders.update({k: str(v) for k, v in load_json(args.placeholders_json).items()})

    render_report(placeholders, args.output)
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
