#!/usr/bin/env bash
set -euo pipefail
root="control-plane/onboarding-service"

mkdir -p "$root/app/api/v1" "$root/app/api/v2" \
         "$root/app/domain" "$root/app/infra/adapters" \
         "$root/openapi" "$root/tests/api/v1" "$root/tests/api/v2"

# Minimal main.py (idempotent)
cat > "$root/app/main.py" <<'PY'
from fastapi import FastAPI, APIRouter

app = FastAPI(title="Onboarding Service")

# v1 stub
v1 = APIRouter()
@v1.get("/tenants")
async def list_tenants_v1(): return {"version":"v1","items":[]}
app.include_router(v1, prefix="/api/v1", tags=["v1-tenants"])

# v2 stub
v2 = APIRouter()
@v2.get("/tenants")
async def list_tenants_v2(): return {"version":"v2","items":[]}
app.include_router(v2, prefix="/api/v2", tags=["v2-tenants"])
PY

# Placeholders so git tracks dirs
touch "$root/app/api/v1/schemas.py" "$root/app/api/v2/schemas.py"
touch "$root/app/domain/services.py" "$root/app/domain/models.py"
touch "$root/app/infra/repositories.py" "$root/app/infra/security.py" "$root/app/infra/idempotency.py"
touch "$root/app/infra/adapters/"{base.py,aws.py,azure.py,gcp.py}
touch "$root/openapi/onboarding.v1.yaml" "$root/openapi/onboarding.v2.yaml"
cat > "$root/tests/api/v1/test_smoke.py" <<'PY'
def test_v1_smoke(): assert True
PY
cat > "$root/tests/api/v2/test_smoke.py" <<'PY'
def test_v2_smoke(): assert True
PY

echo "✅ onboarding versioned skeleton created."