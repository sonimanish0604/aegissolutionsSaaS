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
