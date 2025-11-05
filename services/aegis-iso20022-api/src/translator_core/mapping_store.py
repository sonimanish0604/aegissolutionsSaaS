from pathlib import Path
import json
import re
import yaml

_COMMENT_LINE = re.compile(r"^\s*//.*$", re.MULTILINE)
_COMMENT_BLOCK = re.compile(r"/\*.*?\*/", re.DOTALL)
# Remove trailing commas before } or ]
_TRAILING_COMMA = re.compile(r",(?=\s*[}\]])")

def _relaxed_json_load(text: str):
    """Allow // and /* */ comments, and trailing commas. Fallback for mapping files."""
    no_block = _COMMENT_BLOCK.sub("", text)
    no_line = _COMMENT_LINE.sub("", no_block)
    no_trailing = _TRAILING_COMMA.sub("", no_line)
    return json.loads(no_trailing)

def _load_json_with_diagnostics(path: Path):
    # utf-8-sig handles BOM if present
    raw = path.read_text(encoding="utf-8-sig")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e1:
        # Try relaxed parsing (comments / trailing commas)
        try:
            return _relaxed_json_load(raw)
        except Exception as e2:
            # Build a helpful diagnostics message with context lines
            lines = raw.splitlines()
            ln = getattr(e1, "lineno", None)
            col = getattr(e1, "colno", None)
            start = max(0, (ln or 1) - 3)
            end = min(len(lines), (ln or 1) + 2)
            context = "\n".join(f"{i+1:>5}: {lines[i]}" for i in range(start, end))
            raise ValueError(
                f"Failed to parse mapping JSON: {path}\n"
                f"JSON error at line {ln}, column {col}: {e1.msg}\n\n"
                f"Context:\n{context}\n\n"
                f"Tip: Remove comments and trailing commas, or keep the file strictly valid JSON."
            ) from e1

class MappingStore:
    def __init__(
        self,
        mappings_dir: str = "mappings",
        pairs_yaml: str = "iso-bootstrap/pairs.yaml",
        service_root: Path | None = None,
    ):
        # ... (keep your existing __init__ exactly as we set earlier)
        if service_root is None:
            service_root = Path(__file__).resolve().parents[2]
        self.service_root = service_root
        self.mappings_dir = self.service_root / mappings_dir
        self.pairs_yaml_path = self.service_root / pairs_yaml
        if not self.pairs_yaml_path.exists():
            raise FileNotFoundError(
                f"pairs.yaml not found: {self.pairs_yaml_path}\n"
                f"Expected service root: {self.service_root}"
            )
        with open(self.pairs_yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if isinstance(data, list):
            self.pairs = {"pairs": data}
        elif isinstance(data, dict):
            self.pairs = data if "pairs" in data else {"pairs": data.get("pairs", [])}
        else:
            self.pairs = {"pairs": []}

    def resolve(self, mt_type: str, variant: str | None = None):
        candidates = [p for p in self.pairs.get("pairs", []) if p.get("mt_code") == mt_type]
        if variant is not None:
            for p in candidates:
                if p.get("variant") == variant:
                    return p.get("out_json"), p.get("target_version"), p.get("xsd_dir")
        for p in candidates:
            if not p.get("variant"):
                return p.get("out_json"), p.get("target_version"), p.get("xsd_dir")
        return None, None, None

    def load_profile(self, mt_type: str, variant: str | None = None):
        out_json_rel, mx_type, xsd_dir_rel = self.resolve(mt_type, variant)
        if out_json_rel is None and variant is not None:
            out_json_rel, mx_type, xsd_dir_rel = self.resolve(mt_type)
        if not out_json_rel:
            return None, None, None

        mapping_path = (
            Path(out_json_rel)
            if Path(out_json_rel).is_absolute()
            else (self.service_root / out_json_rel)
        )
        xsd_dir_path = (
            Path(xsd_dir_rel)
            if xsd_dir_rel and Path(xsd_dir_rel).is_absolute()
            else (self.service_root / (xsd_dir_rel or ""))
        )

        if not mapping_path.exists():
            raise FileNotFoundError(
                f"Mapping JSON not found: {mapping_path}\n"
                f"(from pairs.yaml out_json='{out_json_rel}', service_root='{self.service_root}')"
            )
        if xsd_dir_rel and not xsd_dir_path.exists():
            xsd_dir_path = None

        mapping = _load_json_with_diagnostics(mapping_path)
        if not isinstance(mapping, dict):
            raise ValueError(f"Mapping must be a JSON object at top-level: {mapping_path}")
        return mapping, mx_type, str(xsd_dir_path) if xsd_dir_path else None
