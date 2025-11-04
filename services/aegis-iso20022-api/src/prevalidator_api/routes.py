from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..prevalidator_core import PrevalidationEngine

router = APIRouter(prefix="/prevalidate", tags=["prevalidate"])
engine = PrevalidationEngine()


class PrevalidateRequest(BaseModel):
    mt_raw: str
    force_type: str | None = None


@router.post("", summary="Prevalidate an MT message")
def prevalidate(req: PrevalidateRequest):
    if not req.mt_raw or not req.mt_raw.strip():
        raise HTTPException(status_code=400, detail="mt_raw must not be empty")
    result = engine.validate(req.mt_raw, force_type=req.force_type)
    return result.to_dict()
