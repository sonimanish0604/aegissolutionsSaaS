from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict

class CreateTenantRequest(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    source: str
    product_codes: Optional[List[str]] = None
    plan: Optional[str] = None
    marketplace_ctx: Optional[Dict[str, object]] = None

class TenantResponse(BaseModel):
    tenant_id: str
    tenant_slug: str
    status: str
    plan: Optional[str] = None
    products: Optional[list] = None