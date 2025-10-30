from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class CheckResult:
    name: str
    command: List[str]
    passed: bool
    return_code: int
    stdout: str
    stderr: str
    duration_seconds: float


def _run_command(name: str, command: List[str], cwd: Optional[Path] = None) -> CheckResult:
    start = datetime.now(timezone.utc)
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=str(cwd) if cwd else None,
        )
        end = datetime.now(timezone.utc)
        duration = (end - start).total_seconds()
        return CheckResult(
            name=name,
            command=command,
            passed=proc.returncode == 0,
            return_code=proc.returncode,
            stdout=proc.stdout.strip(),
            stderr=proc.stderr.strip(),
            duration_seconds=duration,
        )
    except FileNotFoundError as exc:
        end = datetime.now(timezone.utc)
        duration = (end - start).total_seconds()
        return CheckResult(
            name=name,
            command=command,
            passed=False,
            return_code=127,
            stdout="",
            stderr=str(exc),
            duration_seconds=duration,
        )


def generate_report(
    output: Path,
    enable_pytest: bool = True,
    enable_tooling: bool = True,
) -> None:
    checks: List[CheckResult] = []

    service_root = Path(__file__).resolve().parent.parent
    repo_root = service_root.parent

    if enable_pytest:
        checks.append(
            _run_command(
                "pytest",
                ["pytest", "-q"],
                cwd=service_root,
            )
        )

    if enable_tooling:
        commands = [
            (
                "gitleaks",
                [
                    "gitleaks",
                    "detect",
                    "--no-banner",
                    "--no-git",
                    "--source",
                    str(repo_root),
                ],
            ),
            (
                "semgrep",
                [
                    "semgrep",
                    "scan",
                    "--config",
                    "auto",
                    "--error",
                    "--quiet",
                    str(repo_root),
                ],
            ),
            (
                "syft",
                [
                    "syft",
                    str(repo_root),
                    "-o",
                    "json",
                ],
            ),
            (
                "grype",
                [
                    "grype",
                    f"dir:{repo_root}",
                    "--fail-on",
                    "high",
                    "-o",
                    "json",
                ],
            ),
        ]

        for name, cmd in commands:
            checks.append(_run_command(name, cmd, cwd=repo_root))

    now = datetime.now(timezone.utc)
    git_commit = (
        subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        if shutil.which("git")
        else None
    )

    report = {
        "generated_at": now.isoformat(),
        "git": {
            "commit": git_commit,
            "branch": os.getenv("GITHUB_REF", os.getenv("BRANCH_NAME")),
        },
        "environment": {
            "python": sys.version,
            "hostname": socket.gethostname(),
            "runner": os.getenv("GITHUB_RUN_ID"),
        },
        "checks": [asdict(check) for check in checks],
    }

    summary = {
        "passed": all(check["passed"] for check in report["checks"]),
        "failed_checks": [check["name"] for check in report["checks"] if not check["passed"]],
        "total_checks": len(report["checks"]),
    }
    report["summary"] = summary

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"SOC2 compliance report written to {output}")
    if not summary["passed"]:
        raise SystemExit("One or more SOC2 compliance checks failed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SOC2 compliance checks and emit a report.")
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the JSON report to write.",
    )
    parser.add_argument(
        "--skip-pytest",
        action="store_true",
        help="Skip running pytest (not recommended).",
    )
    parser.add_argument(
        "--skip-security-tools",
        action="store_true",
        help="Skip running gitleaks/semgrep/syft/grype (for local debugging only).",
    )
    args = parser.parse_args()

    output_path = Path(args.output).resolve()
    enable_pytest = not args.skip_pytest
    enable_tools = not args.skip_security_tools
    generate_report(
        output_path,
        enable_pytest=enable_pytest,
        enable_tooling=enable_tools,
    )


if __name__ == "__main__":
    main()
