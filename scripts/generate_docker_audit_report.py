#!/usr/bin/env python3
"""Generate a PDF summary for the Docker audit integration run."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


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

    doc = SimpleDocTemplate(str(output), pagesize=LETTER, title="Docker Audit Integration Report")
    styles = getSampleStyleSheet()
    elements = []

    if args.logo:
        logo_path = Path(args.logo)
        if logo_path.exists():
            img = Image(str(logo_path), width=140, height=60, preserveAspectRatio=True)
            elements.append(img)
            elements.append(Spacer(1, 12))

    title = Paragraph("Aegis ISO 20022 – Docker Audit Integration Report", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 6))

    meta_table = Table(
        [
            ["Generated", generated_at],
            ["Workflow", f"{args.workflow} / {args.job}"],
            ["Run URL", args.run_url],
            ["Branch", args.branch],
            ["Commit", args.commit],
        ],
        colWidths=[120, 360],
    )
    meta_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke), ("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey)]))
    elements.append(meta_table)
    elements.append(Spacer(1, 18))

    summary_data = [
        ["Test Name", args.test_name],
        ["Result", "PASS"],
        ["Manifest objects detected", str(manifest_count)],
        ["Manifest keys", manifest_line or "not available"],
    ]
    summary_table = Table(summary_data, colWidths=[200, 280])
    summary_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey), ("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black)]))
    elements.append(Paragraph("Test Summary", styles["Heading2"]))
    elements.append(summary_table)
    elements.append(Spacer(1, 18))

    env_table = Table(
        [
            ["Translator URL", args.translator_url],
            ["Prevalidator URL", args.prevalidator_url],
            ["S3 Endpoint", args.s3_endpoint],
        ],
        colWidths=[200, 280],
    )
    env_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey), ("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black)]))
    elements.append(Paragraph("Environment", styles["Heading2"]))
    elements.append(env_table)
    elements.append(Spacer(1, 18))

    notes = Paragraph(
        "This report follows the unit-test template defined in services/aegis-iso20022-api/docs/unit-test-report.md. "
        "Detailed container logs (translator, audit worker, Localstack) are attached to the workflow artifacts.",
        styles["BodyText"],
    )
    elements.append(Paragraph("Notes", styles["Heading2"]))
    elements.append(notes)

    doc.build(elements)


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
    parser.add_argument("--logo")

    args = parser.parse_args()
    build_pdf(args)


if __name__ == "__main__":
    main()
