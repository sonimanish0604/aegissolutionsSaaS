# Change Management Controls Mapping

This document lists the evidence sources auditors can reference for each change management requirement.

| Requirement                         | Evidence Source                                                                 |
|-------------------------------------|----------------------------------------------------------------------------------|
| Change initiated by request         | GitHub Issue (includes description, risk, rollback)                              |
| Change reviewed & approved          | Pull Request (approved review entries, branch protections)                       |
| Change tested before release        | CI logs, attached test artifacts (unit, regression, security scans)              |
| Change traceability (Issue → Code)  | PR description with “Closes #X”, commits referencing issue IDs                  |
| Change immutably logged             | Change manifest (`manifest.json`/`manifest.sig`) stored in S3 Object Lock        |
| Accountability / identity preserved | Git commit signature or PR merge user identity recorded in the manifest/logs    |
| Cloud/API access logging            | Terraform outputs for CloudTrail trail/bucket per environment (testing/stage/prod) |

Use this mapping during audits to gather the appropriate evidence for each change.
