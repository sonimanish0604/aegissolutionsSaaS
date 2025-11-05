from __future__ import annotations

import functools
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

ROOT_DIR = Path(__file__).resolve().parents[2]
PREVALIDATE_DIR = ROOT_DIR / "pre-validateMT"
LOOKUPS_FILE = PREVALIDATE_DIR / "lookups.yaml"

ALIASES = {
    "MT195": "MTn95",
    "MT196": "MTn96",
}


class FieldDefinitionsLoader:
    """Loads field validation metadata for MT messages."""

    def __init__(self) -> None:
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        self._lookups: Optional[Dict[str, Any]] = None

    def get_definitions(self, mt_type: str) -> Optional[List[Dict[str, Any]]]:
        mt_type = mt_type.upper()
        if mt_type in self._cache:
            return self._cache[mt_type]
        folder = ALIASES.get(mt_type, mt_type)
        path = PREVALIDATE_DIR / folder / "fieldvalidations.yaml"
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or []
        if not isinstance(data, list):
            raise ValueError(f"Unexpected field validations structure for {mt_type}")
        self._cache[mt_type] = data
        return data

    @functools.lru_cache(maxsize=1)
    def get_lookups(self) -> Dict[str, Any]:
        if not LOOKUPS_FILE.exists():
            return {}
        with LOOKUPS_FILE.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            raise ValueError("Invalid lookups.yaml structure")
        return data
