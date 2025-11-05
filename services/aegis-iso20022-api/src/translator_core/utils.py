from decimal import Decimal, InvalidOperation
import re
from datetime import datetime

def safe_decimal(s: str) -> Decimal | None:
    s = s.strip().replace(",", ".")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None

def parse_yyMMdd(s: str) -> str | None:
    # SWIFT 32A date is YYMMDD
    try:
        dt = datetime.strptime(s, "%y%m%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None

IBAN_RE = re.compile(r"^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$")
BIC_RE  = re.compile(r"^[A-Z]{6}[A-Z2-9][A-NP-Z0-9]([A-Z0-9]{3})?$")