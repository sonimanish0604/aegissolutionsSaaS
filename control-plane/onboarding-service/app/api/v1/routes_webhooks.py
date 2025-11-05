from fastapi import APIRouter, Request, HTTPException, status

router = APIRouter()

@router.post("/webhooks/{provider}")
async def webhook(provider: str, request: Request):
    if provider not in ("aws", "azure", "gcp"):
        raise HTTPException(status_code=404, detail="provider not supported")
    payload = await request.json()
    # TODO: signature verification + normalization + enqueue for processing
    return {"status": "accepted"}