# Manifest Verification Procedure

This procedure describes how to verify the integrity and authenticity of the hourly audit manifests stored in `s3://aegis-audit-archive`.

## Prerequisites

- AWS CLI configured (with access to the audit archive bucket and KMS key)
- IAM permissions: `s3:GetObject`, `kms:VerifyMac`
- Knowledge of the partition path (e.g., `dt=2025/10/31/09/tenant_id=TEN123`)

## Steps

1. Download the manifest and signature:
   ```bash
   aws s3 cp s3://aegis-audit-archive/dt=YYYY/MM/DD/HH/tenant_id=TEN123/MANIFEST.json ./
   aws s3 cp s3://aegis-audit-archive/dt=YYYY/MM/DD/HH/tenant_id=TEN123/MANIFEST.sig ./
   ```

2. Verify the KMS signature:
   ```bash
   aws kms verify-mac \
     --key-id arn:aws:kms:REGION:ACCOUNT:key/KEY_ID \
     --mac-algorithm HMAC_SHA_256 \
     --message fileb://MANIFEST.json \
     --mac fileb://MANIFEST.sig
   ```

3. Confirm the response shows `"MacValid": true`. Any failure indicates the manifest was tampered with or signed with an unexpected key.

## Optional (dev/test)

For local testing without KMS:

```python
from audit_integrity.signer import LocalHmacSigner
payload = Path("MANIFEST.json").read_bytes()
signature = Path("MANIFEST.sig").read_text().strip()
assert LocalHmacSigner(b"test-secret").sign(payload) == signature
```

Keep this verification as part of the daily integrity Lambda and your compliance evidence.
