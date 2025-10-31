from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest
import requests

pytest.importorskip("requests")

TRANSLATOR_URL = os.getenv("TRANSLATOR_URL", "http://localhost:8080")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")


@pytest.mark.integration
@pytest.mark.timeout(120)
def test_translate_emits_kafka_event(tmp_path):
    payload = {
        "mt_raw": "{1:F01BANKDEFFXXXX0000000000}{2:I101BANKUS33XXXXN}{4:\n:20:REF20251022A\n:28D:1/1\n:50H:/DE44500105175407324931\nMAX MUSTERMANN\n1 MAIN STREET\nEPPING\nGB\n:30:20251022\n:21:INV-5568\n:32B:USD12345,67\n:57A:BANKUS33XXX\n:59:/US12300099900011122\nJOHN DOE\n742 EVERGREEN TERRACE\nSPRINGFIELD IL 62704\nUS\n:70:/INV/5568 NET30\n:71A:SHA\n-}"
    }

    response = requests.post(
        f"{TRANSLATOR_URL}/translate", json=payload, timeout=15
    )
    response.raise_for_status()

    # Consume from Kafka for the event
    consumer_cmd = [
        "kafka-console-consumer",
        "--bootstrap-server",
        KAFKA_BOOTSTRAP,
        "--topic",
        "audit.events",
        "--max-messages",
        "1",
        "--timeout-ms",
        "5000",
        "--from-beginning",
    ]

    from subprocess import run, PIPE

    result = run(consumer_cmd, check=False, stdout=PIPE, stderr=PIPE, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip(), "No audit event received"

    event = json.loads(result.stdout.splitlines()[-1])
    assert event["type"] == "api_call"
    assert event["route"] == "/translate"
    assert event["tenant_id"] == ""
    assert event["event_id"]
