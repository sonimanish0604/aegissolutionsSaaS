from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

CURRENT = Path(__file__).resolve().parent
ROOT = CURRENT.parent

for path in (ROOT, CURRENT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from src.translator_api.routes import app  # noqa: E402  pylint: disable=wrong-import-position
import json

SAMPLE_BATCH = ROOT / "batch-mode-samples" / "MTBatch_20251030.dat"


@pytest.mark.skipif(not SAMPLE_BATCH.exists(), reason="sample batch file missing")
def test_translate_batch_json_response():
    client = TestClient(app)
    data = SAMPLE_BATCH.read_bytes()
    response = client.post(
        "/translate/batch",
        files={"file": ("MTBatch_20251030.dat", data, "application/octet-stream")},
        params={"responseFileFormat": "json"},
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["summary"]["total_batches"] == 1
    assert payload["summary"]["total_messages"] == 3
    assert payload["summary"]["failed"] == 0
    assert "processed_at" in payload["summary"]

    batch = payload["batches"][0]
    assert batch["summary"]["succeeded"] == 3
    for result in batch["results"]:
        assert result["status"] == "ok"
        assert result["mx_type"]
        assert "<Document" in result["xml"]
        assert result["xml_validator"]


@pytest.mark.skipif(not SAMPLE_BATCH.exists(), reason="sample batch file missing")
def test_translate_batch_zip_response():
    client = TestClient(app)
    data = SAMPLE_BATCH.read_bytes()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("batch/sample.dat", data)
    buffer.seek(0)

    response = client.post(
        "/translate/batch",
        files={"file": ("multi.zip", buffer.read(), "application/zip")},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert "attachment" in response.headers.get("content-disposition", "")

    archive = io.BytesIO(response.content)
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        assert "summary.json" in names
        summary = json.loads(zf.read("summary.json"))
        assert summary["summary"]["total_messages"] == 3
        assert "generated_at" in summary
        xml_entries = [name for name in names if name.endswith(".xml")]
        assert len(xml_entries) == 3
        error_entries = [name for name in names if name.endswith("_error.json")]
        assert not error_entries


def test_translate_batch_rejects_unsupported_type():
    client = TestClient(app)
    response = client.post(
        "/translate/batch",
        files={"file": ("bad.bin", b"\x00\x01\x02", "application/octet-stream")},
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Unsupported file type" in detail
