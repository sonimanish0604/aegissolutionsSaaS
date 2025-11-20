from __future__ import annotations

import sys
from pathlib import Path

import pytest

CURRENT = Path(__file__).resolve().parent
ROOT = CURRENT.parent

for path in (ROOT, CURRENT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from category1_samples import CATEGORY1_SAMPLES as SAMPLES
from src.prevalidator_core import PrevalidationEngine


@pytest.mark.parametrize("label", sorted(SAMPLES.keys()))
def test_category1_samples_are_valid(label: str) -> None:
    sample = SAMPLES[label]
    engine = PrevalidationEngine()
    kwargs = {}
    force_type = sample.get("force_type")
    if force_type:
        kwargs["force_type"] = force_type
    result = engine.validate(sample["mt_raw"], **kwargs)
    expected_type = force_type or label
    assert result.mt_type == expected_type, f"{label} detected as {result.mt_type}"
    assert result.valid, f"{label} should be valid but returned errors: {result.errors}"
    assert not result.errors
    assert not result.warnings
