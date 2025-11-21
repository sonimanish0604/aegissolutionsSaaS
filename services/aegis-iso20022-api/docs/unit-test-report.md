![Aegis Logo](aegislogo.png)

# Aegis Test Report Template

Use this structure for every automated test evidence packet.

## Header
- **Title** – e.g., “Aegis ISO 20022 – Docker Audit Integration Report”
- **Generated** – UTC timestamp
- **Workflow / Job** – GitHub workflow + job name
- **Run URL** – hyperlink to the workflow execution
- **Branch / Commit** – source branch and short SHA

## Test Summary
| Field | Description |
| ----- | ----------- |
| Test Name | Scenario identifier (unit, integration, smoke, etc.) |
| Result | PASS / FAIL |
| Metrics | Include counts, artifacts, manifest identifiers, or timings |

## Environment
| Field | Value |
| ----- | ----- |
| Translator URL | Example: `http://localhost:8080` |
| Supporting Services | Prevalidator, worker, etc. |
| Storage Endpoint | S3/Localstack URL for artifacts |

## Notes
- Mention that detailed logs and manifests are attached.
- Record any deviations, manual steps, or follow-up actions.

The automation in `scripts/generate_docker_audit_report.py` uses this template to
format PDF evidence with the logo, header, summary, environment details, and notes.
