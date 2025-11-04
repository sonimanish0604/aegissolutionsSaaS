from __future__ import annotations

import datetime as _dt
import re
from typing import Callable, Dict, Optional, Set

from .loader import FieldDefinitionsLoader

X_CHARSET = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/ -?:().,'+\r\n")

_LOOKUP_CACHE: Dict[str, Set[str]] = {}


RuleFunc = Callable[[str], Optional[str]]


def _ok(_: str) -> Optional[str]:
    return None


def no_leading_or_trailing_slash_or_double_slash(value: str) -> Optional[str]:
    stripped = value.strip()
    if not stripped:
        return None
    lines = stripped.splitlines() or [stripped]
    for line in lines:
        if line.startswith("/"):
            return "Value must not start with '/'"
        if line.endswith("/"):
            return "Value must not end with '/'"
        if "//" in line:
            return "Value must not contain consecutive slashes"  # double slash
    return None


def must_be_valid_date_yymmdd(value: str) -> Optional[str]:
    match = re.match(r"^(\d{8}|\d{6})", value)
    if not match:
        return "Expected leading date in YYMMDD or YYYYMMDD format"
    try:
        token = match.group(1)
        fmt = "%y%m%d" if len(token) == 6 else "%Y%m%d"
        _dt.datetime.strptime(token, fmt)
    except ValueError:
        return "Invalid date value"
    return None


def currency_must_be_valid_iso4217(value: str) -> Optional[str]:
    match = re.search(r"([A-Z]{3})", value)
    if not match:
        return "Currency code not found"
    return None


def amount_integer_part_at_least_one_digit(value: str) -> Optional[str]:
    match = re.search(r"([0-9]{1,})(?:[,.][0-9]*)?$", value.strip())
    if not match:
        return "Missing integer amount component"
    return None


def amount_decimal_comma_mandatory(value: str) -> Optional[str]:
    if "," not in value:
        return "Decimal comma is mandatory"
    return None


def amount_decimal_places_within_currency_precision(value: str) -> Optional[str]:
    if "," not in value:
        return None
    decimals = value.split(",", 1)[1]
    decimals = re.sub(r"[^0-9]", "", decimals)
    if len(decimals) > 15:
        return "Decimal part exceeds 15 digits"
    return None


def payee_account_must_not_be_present(value: str) -> Optional[str]:
    first_line = value.strip().splitlines()[0] if value.strip() else ""
    if first_line.startswith("/"):
        return "Account line is not permitted"
    return None


def value_must_use_x_charset(value: str) -> Optional[str]:
    for ch in value:
        if ch not in X_CHARSET:
            return f"Character '{ch}' not allowed in X charset"
    return None


def mt_number_and_date(value: str) -> Optional[str]:
    if value is None:
        return None
    tokens = value.strip().split()
    if len(tokens) < 2:
        return "Expected MT number and YYMMDD date"
    mt_code, date_token = tokens[0], tokens[1]
    if not re.fullmatch(r"\d{3}", mt_code):
        return "MT number must be three digits"
    mt_int = int(mt_code)
    if not 100 <= mt_int <= 999:
        return "MT number must be between 100 and 999"
    if not re.fullmatch(r"\d{6}", date_token):
        return "Date must be expressed as YYMMDD"
    try:
        _dt.datetime.strptime(date_token, "%y%m%d")
    except ValueError:
        return "Invalid date value"
    return None


def _lookup_codes(name: str) -> Set[str]:
    if name in _LOOKUP_CACHE:
        return _LOOKUP_CACHE[name]
    loader = FieldDefinitionsLoader()
    lookups = loader.get_lookups()
    values = lookups.get(name, {}) if isinstance(lookups, dict) else {}
    codes = {code.upper() for code in values.keys()}
    _LOOKUP_CACHE[name] = codes
    return codes


def mt196_rjcr_pdcr_reason_codes(value: str) -> Optional[str]:
    if not value:
        return None
    text = value.upper()
    if "RJCR" not in text and "PDCR" not in text:
        return None
    codes = _lookup_codes("mt196_reason_codes")
    if not codes:
        return None
    pattern = r"\b(" + "|".join(re.escape(code) for code in sorted(codes, key=len, reverse=True)) + r")\b"
    if re.search(pattern, text):
        return None
    return "Reason code required when RJCR or PDCR is reported"


RULES: Dict[str, RuleFunc] = {
    "no_leading_or_trailing_slash_or_double_slash": no_leading_or_trailing_slash_or_double_slash,
    "must_be_valid_date_yymmdd": must_be_valid_date_yymmdd,
    "currency_must_be_valid_iso4217": currency_must_be_valid_iso4217,
    "amount_integer_part_at_least_one_digit": amount_integer_part_at_least_one_digit,
    "amount_decimal_comma_mandatory": amount_decimal_comma_mandatory,
    "amount_decimal_places_within_currency_precision": amount_decimal_places_within_currency_precision,
    "payee_account_must_not_be_present": payee_account_must_not_be_present,
    "value_must_use_x_charset": value_must_use_x_charset,
    "mt_number_and_date": mt_number_and_date,
    "mt196_rjcr_pdcr_reason_codes": mt196_rjcr_pdcr_reason_codes,
}


def apply_rule(rule_name: str, value: str) -> Optional[str]:
    func = RULES.get(rule_name, _ok)
    return func(value)
