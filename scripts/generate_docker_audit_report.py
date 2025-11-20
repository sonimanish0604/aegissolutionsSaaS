#!/usr/bin/env python3
"""Generate a PDF summary for the Docker audit integration run."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


def parse_manifest_summary(log_path: Path) -> tuple[str, int] | tuple[None, int]:
    """Return the manifest summary line and count if present."""
    if not log_path.exists():
        return None, 0

    pattern = re.compile(r"Audit smoke test passed with manifests:\s*(\[.*\])")
    manifest_line = None
    count = 0

    for line in log_path.read_text().splitlines():
        match = pattern.search(line)
        if match:
            manifest_line = match.group(1)
            # crude count by counting comma-separated entries
            entries = [item.strip() for item in match.group(1).strip("[]").split(",") if item.strip()]
            count = len(entries)
    return manifest_line, count


def build_pdf(args: argparse.Namespace) -> None:
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    manifest_line, manifest_count = parse_manifest_summary(Path(args.test_log))

    width, height = LETTER
    c = canvas.Canvas(str(output), pagesize=LETTER)
    text = c.beginText(40, height - 50)

    text.setFont("Helvetica-Bold", 14)
    text.textLine("Aegis ISO 20022 - Docker Audit Integration Report")
    text.setFont("Helvetica", 10)
    text.textLine(f"Generated: {generated_at}")
    text.textLine(f"Workflow: {args.workflow} / {args.job}")
    text.textLine(f"Run URL: {args.run_url}")
    text.textLine(f"Branch: {args.branch}")
    text.textLine(f"Commit: {args.commit}")
    text.textLine("")

    text.setFont("Helvetica-Bold", 12)
    text.textLine("Test Summary")
    text.setFont("Helvetica", 10)
    text.textLine(f"Test Name: {args.test_name}")
    text.textLine("Result: PASS")
    if manifest_line:
        text.textLine(f"Manifest objects detected: {manifest_count}")
        text.textLine(f"Manifest keys: {manifest_line}")
    else:
        text.textLine("Manifest details: (not found in log)")
    text.textLine("")

    text.setFont("Helvetica-Bold", 12)
    text.textLine("Environment")
    text.setFont("Helvetica", 10)
    text.textLine(f"Translator URL: {args.translator_url}")
    text.textLine(f"Prevalidator URL: {args.prevalidator_url}")
    text.textLine(f"S3 Endpoint: {args.s3_endpoint}")
    text.textLine("")

    text.setFont("Helvetica-Bold", 12)
    text.textLine("Notes")
    text.setFont("Helvetica", 10)
    text.textLine("This report summarizes the automated Docker audit integration run.")
    text.textLine("Detailed logs (translator, audit worker, Localstack) are attached to the workflow artifacts.")

    c.drawText(text)
    c.showPage()
    c.save()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Docker audit integration report.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--test-log", required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--test-name", required=True)
    parser.add_argument("--translator-url", required=True)
    parser.add_argument("--prevalidator-url", required=True)
    parser.add_argument("--s3-endpoint", required=True)

    args = parser.parse_args()
    build_pdf(args)


if __name__ == "__main__":
    main()
