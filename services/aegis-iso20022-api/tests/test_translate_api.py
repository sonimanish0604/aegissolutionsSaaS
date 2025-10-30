from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

CURRENT = Path(__file__).resolve().parent
ROOT = CURRENT.parent

for path in (ROOT, CURRENT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from category1_samples import SAMPLES  # noqa: E402  pylint: disable=wrong-import-position
from src.translator_api.routes import TranslateRequest, translate  # noqa: E402  pylint: disable=wrong-import-position


def test_translate_prevalidation_succeeds():
    request = TranslateRequest(mt_raw=SAMPLES["MT101"]["mt_raw"])
    response = translate(request)
    assert response["validation"]["ok"] is True
    assert response["mx_type"]


def test_translate_prevalidation_failure_raises_http_exception():
    invalid_mt = "{1:F01BANKUS33AXXX0000000000}{2:I101BANKUS33XXXXN}{4:\n-}"
    request = TranslateRequest(mt_raw=invalid_mt)
    with pytest.raises(HTTPException) as excinfo:
        translate(request)
    assert excinfo.value.status_code == 422
    detail = excinfo.value.detail
    assert detail["message"] == "Prevalidation failed"
    assert detail["result"]["valid"] is False
    assert detail["result"]["errors"]


def test_translate_allows_disabling_prevalidation():
    request = TranslateRequest(mt_raw=SAMPLES["MT101"]["mt_raw"], prevalidate=False)
    response = translate(request)
    assert response["validation"]["ok"] is True
