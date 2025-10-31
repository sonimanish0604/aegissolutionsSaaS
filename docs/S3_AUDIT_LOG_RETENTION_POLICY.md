# S3 Audit Log Retention Policy

## Summary

Aegis maintains immutable audit logs in Amazon S3 for **7 years** to satisfy ISO 27001 A.12.4, PCI DSS Req. 10, and SWIFT CSP 4.2. Logs remain locked (Object Lock – Compliance mode) for the entire retention period and are streamed to customers’ SIEM platforms in near real time for operational monitoring.

## Retention & Lifecycle

- Retention period: 7 years (2555 days)
- Object Lock: Compliance mode with legal hold support
- Lifecycle transitions:
  - < 3 years: Standard storage class (frequent access)
  - ≥ 3 years: transition to Glacier Deep Archive to optimize cost
- Automatic deletion at 7 years (Object Lock expiration)

## Policy statement

> “Aegis ISO20022 API maintains immutable audit logs for 7 years in compliance with ISO 27001 A.12.4, PCI DSS 10, and SWIFT CSP 4.2. Logs are streamed to the customer’s SIEM in near real time.”

## Implementation notes

- Bucket: `s3://aegis-audit-archive`
- Encryption: SSE-KMS with dedicated audit key
- Manifest & signature stored alongside data (`MANIFEST.json` / `MANIFEST.sig`)
- Lifecycle management defined in Terraform – see Appendix for sample
- Verification Lambda runs daily to ensure integrity

## Appendix (sample Terraform snippet)

```hcl
resource "aws_s3_bucket" "audit_archive" {
  bucket = "aegis-audit-archive"
  object_lock_configuration {
    rule {
      default_retention {
        mode = "COMPLIANCE"
        days = 2555
      }
    }
  }

  lifecycle_rule {
    id      = "GlacierAfterThreeYears"
    enabled = true

    transition {
      days          = 1095
      storage_class = "GLACIER_DEEP_ARCHIVE"
    }

    expiration {
      days = 2555
    }
  }
}
```
