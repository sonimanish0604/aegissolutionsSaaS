# Audit Log Data Access Procedure

## Purpose

Describe how auditors or investigators retrieve tenant-specific audit data from the Aegis audit archive while preserving access controls and chain of custody.

## Governance

- Access requires approval from the Control Owner and Information Security Officer.
- Data is tenant-scoped; analysts may only access partitions for the tenant under review.
- All access is logged (CloudTrail), and KMS key grants are time-bound.

## Steps

1. **Identify scope**
   - Tenant ID: `TEN123`
   - Date range: `2025-10-01` to `2025-10-31`
   - Relevant partition prefix: `dt=YYYY/MM/DD/HH/tenant_id=TEN123`

2. **Grant temporary IAM/KMS permissions**
   - Issue a time-limited IAM role or access key with the following permissions:
     - `s3:GetObject`, `s3:ListBucket` for `s3://aegis-audit-archive/dt=.../tenant_id=TEN123/*`
     - `kms:GenerateMac` and `kms:VerifyMac` for the audit key
   - Optionally provide their SIEM ingestion role if they need streaming access

3. **Retrieve data**
   - List objects: `aws s3 ls s3://aegis-audit-archive/dt=2025/10/01/00/tenant_id=TEN123/`
   - Download an object: `aws s3 cp s3://.../part-0000.parquet ./`
   - Download manifest and signature for each hour (see Manifest Verification Procedure)
   - Optional: use AWS Athena with external table to run SQL queries scoped to the tenant

4. **Verify manifest signature**
   - Follow [Manifest Verification Procedure](S3_MANIFEST_VERIFICATION.md) to confirm integrity and authenticity

5. **Provide evidence**
   - Supply `MANIFEST.json`, `MANIFEST.sig`, and object list to auditors
   - Collect CloudTrail events (`kms:GenerateMac`, `s3:GetObject`) as part of the evidence package

6. **Revoke access**
   - After the review, remove IAM grants or expire the session tokens

## Notes

- Real-time logs continue to stream to the tenant SIEM
- Aegis does not share raw keys; all signing uses AWS KMS
- For large exports, consider S3 Select or Athena CTAS to aggregate results
