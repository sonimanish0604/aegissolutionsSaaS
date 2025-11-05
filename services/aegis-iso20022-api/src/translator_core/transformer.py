from datetime import datetime
import re
from typing import Any, Dict, List


# ---------- Basic nested-mode helpers (kept for compatibility) ----------

def set_path(root: Dict, path: str, value: Any):
    node = root
    parts = path.split("/")
    for i, part in enumerate(parts):
        is_attr = part.startswith("@")
        if i == len(parts) - 1:
            if is_attr:
                raise ValueError(f"Attribute notation '@{part}' must be on the last segment only")
            node[part] = value
            return
        if is_attr:
            raise ValueError(f"Attribute @{part} not allowed mid-path")
        node = node.setdefault(part, {})

def set_attribute(root: Dict, parent_path: str, attr_name: str, value: Any):
    node = root
    for part in parent_path.split("/"):
        node = node.setdefault(part, {})
    node[f"@{attr_name}"] = value

def get_value(src: Dict, dotted: str):
    """
    Returns the first raw value for an MT tag.
    - If dotted contains a dot (e.g., '32A.amount'), we intentionally DO NOT derive subkeys here.
    - Mapping is responsible to extract via transforms (e.g., regex_extract).
    """
    key = dotted.split(".", 1)[0]
    v = src.get(key)
    if isinstance(v, list):
        return v[0] if v else None
    return v


# ---------- Transform functions & dispatcher ----------

_IBAN_RE = re.compile(r"[^A-Za-z0-9]")

def _transform_to_decimal(v):
    if v is None:
        return None
    s = str(v).strip().replace(" ", "")
    if "," in s and "." not in s:
        int_part, frac_part = s.split(",", 1)
        if frac_part.isdigit():
            s = f"{int_part.replace('.', '').replace(',', '')}.{frac_part}"
        else:
            s = s.replace(",", "")
    else:
        s = s.replace(",", "")
    return s

def _transform_date_parse(v, fmt):
    if v is None: return None
    dt = datetime.strptime(str(v), fmt)
    return dt.strftime("%Y-%m-%d")

def _transform_lines(v):
    if v is None: return None
    if isinstance(v, list): return v
    return [line.strip() for line in str(v).splitlines() if line.strip()]

def _transform_iban_normalize(v):
    if v is None: return None
    iban = _IBAN_RE.sub("", str(v)).upper()
    if 15 <= len(iban) <= 34:
        return iban
    raise ValueError("IBAN normalization failed")

def _transform_truncate(v, max_len):
    if v is None: return None
    s = str(v)
    return s if len(s) <= max_len else s[:max_len]

def _transform_now(_):
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _transform_charge_code(v):
    if v is None:
        return None
    code = str(v).strip().upper()
    return {"BEN": "DEBT", "OUR": "CRED", "SHA": "SHAR"}.get(code, code)

def run_transform(spec, value):
    """
    spec can be:
      - string, e.g. 'to_decimal'
      - object, e.g. {'fn':'date_parse', 'args': {'format':'%y%m%d'}}
      - list of the above, to apply sequentially (pipeline)
    """
    def _apply_one(fn, args, val):
        try:
            if fn == "to_decimal":
                return _transform_to_decimal(val)
            if fn == "date_parse":
                return _transform_date_parse(val, args.get("format", "%y%m%d"))
            if fn == "iban_normalize":
                return _transform_iban_normalize(val)
            if fn == "lines":
                return _transform_lines(val)
            if fn == "truncate":
                return _transform_truncate(val, int(args.get("max", 140)))
            if fn == "upper":
                return str(val).upper() if val is not None else None
            if fn == "now":
                return _transform_now(None)
            if fn == "charge_code":
                return _transform_charge_code(val)
            if fn == "regex_extract":
                # args: pattern (str), group (int or str)
                if val is None:
                    return None
                pattern = args.get("pattern")
                group = args.get("group", 0)
                if not pattern:
                    raise ValueError("regex_extract requires 'pattern'")
                m = re.search(pattern, str(val), flags=re.M | re.S)
                if not m:
                    return None
                return m.group(group)
            raise ValueError(f"Unknown transform: {fn}")
        except Exception as ex:
            raise ex

    if spec is None:
        return value

    if isinstance(spec, list):
        out = value
        for step in spec:
            if isinstance(step, str):
                fn, args = step, {}
            else:
                fn, args = step.get("fn"), step.get("args", {})
            out = _apply_one(fn, args, out)
        return out

    if isinstance(spec, str):
        return _apply_one(spec, {}, value)
    else:
        return _apply_one(spec.get("fn"), spec.get("args", {}), value)


# ---------- Nested-mode apply (kept for compatibility) ----------

def apply_defaults(mx: Dict, defaults: Dict, context: Dict):
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    for path, cfg in (defaults or {}).items():
        v = cfg.get("value")
        if v == "$now": v = now
        if v == "$context.request_id": v = context.get("request_id")
        if "/@" in path:
            parent, attr = path.split("/@")
            set_attribute(mx, parent, attr, v)
        else:
            set_path(mx, path, v)

def _apply_simple_mapping(mt: Dict, mx: Dict, m: Dict, error_policy: str):
    source = m.get("source")
    target = m.get("target")
    transform_spec = m.get("transform")
    on_fail = m.get("on_fail")
    attrs = m.get("attributes") or {}

    raw_val = get_value(mt, source) if source else None
    try:
        out_val = run_transform(transform_spec, raw_val) if transform_spec else raw_val
    except Exception:
        if on_fail:
            if "/@" in on_fail:
                parent, attr = on_fail.split("/@")
                set_attribute(mx, parent, attr, raw_val)
            else:
                set_path(mx, on_fail, raw_val)
            return
        if error_policy == "fail":
            raise
        return

    for k, v in attrs.items():
        val = get_value(mt, v[4:]) if isinstance(v, str) and v.startswith("$mt.") else v
        set_attribute(mx, target, k, val)

    if "/@" in target:
        parent, attr = target.split("/@")
        set_attribute(mx, parent, attr, out_val)
    else:
        set_path(mx, target, out_val)

def apply_mapping(mt: Dict, mapping: Dict, context: Dict | None = None) -> Dict:
    context = context or {}
    mx: Dict = {}

    apply_defaults(mx, mapping.get("defaults"), context)

    error_policy = (mapping.get("error_policies") or {}).get("on_transform_error", "warn_and_copy_raw")
    for block in mapping.get("blocks", []):
        for m in block.get("mappings", []):
            if "switch" in m:
                when_any = m.get("when_any") or []
                if when_any and not any(get_value(mt, w.get("exists","")) is not None for w in when_any):
                    continue
                for br in m.get("switch", []):
                    cond = br.get("if", {})
                    if get_value(mt, cond.get("exists","")) is not None:
                        for mm in br.get("mappings", []):
                            _apply_simple_mapping(mt, mx, mm, error_policy)
                        break
                continue
            _apply_simple_mapping(mt, mx, m, error_policy)

    for val in mapping.get("validations", []):
        if val.get("required"):
            path = val["path"]
            node = mx
            exists = True
            for seg in path.split("/"):
                if seg.startswith("@"):
                    exists = seg in node
                    break
                if seg in node:
                    node = node[seg]
                else:
                    exists = False
                    break
            if not exists or node in (None, "", []):
                raise ValueError(f"Validation failed: required '{path}' is missing")
    return mx


# ---------- Flat-mode emitter for MXBuilder ----------
# -------- Flat mode (for MXBuilder) --------

class _FlatEmitter:
    """Collects values into a flat XPath -> [values] dict that mx_builder expects."""
    def __init__(self, root="FIToFICstmrCdtTrf"):
        self.root = root
        self.flat: Dict[str, list[str]] = {}

    def put(self, rel_path: str, value: Any):
        """Write one or many values to /Document/<root>/<rel_path>."""
        if value is None:
            return
        full = f"/Document/{self.root}/{rel_path}" if rel_path else f"/Document/{self.root}"
        # If it's a list, emit one node per item
        if isinstance(value, list):
            for item in value:
                self.flat.setdefault(full, []).append(str(item))
        else:
            self.flat.setdefault(full, []).append(str(value))

    def put_attr(self, rel_parent: str, attr: str, value: Any):
        if value is None:
            return
        self.put(f"{rel_parent}/@{attr}", value)


def apply_mapping_flat(mt: Dict, mapping: Dict, context: Dict | None = None, mx_root: str = "FIToFICstmrCdtTrf") -> Dict[str, list[str]]:
    """
    Convert MT dict to a flat XPath map using the mapping template.
    Now respects per-block 'target_root' so tx-level nodes land under CdtTrfTxInf.
    """
    context = context or {}
    em = _FlatEmitter(root=mx_root)

    # defaults at the document/root level
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    for path, cfg in (mapping.get("defaults") or {}).items():
        v = cfg.get("value")
        if v == "$now": v = now
        if v == "$context.request_id":
            v = context.get("request_id")
            # sensible fallback so MsgId is never empty
            if v is None and path == "GrpHdr/MsgId":
                v = now
        if "/@" in path:
            parent, attr = path.split("/@")
            em.put_attr(parent, attr, v)
        else:
            em.put(path, v)

    error_policy = (mapping.get("error_policies") or {}).get("on_transform_error", "warn_and_copy_raw")

    def _emit_simple(m: Dict, base: str):
        source = m.get("source")
        target = m.get("target")
        transform_spec = m.get("transform")
        on_fail = m.get("on_fail")
        attrs = m.get("attributes") or {}
        value_lit = m.get("value")  # <-- add

        raw_val = get_value(mt, source) if source else value_lit #None
        try:
            out_val = run_transform(transform_spec, raw_val) if transform_spec else raw_val
        except Exception:
            if on_fail:
                if "/@" in on_fail:
                    parent, attr = on_fail.split("/@")
                    parent_full = f"{base}/{parent}" if base else parent
                    em.put_attr(parent_full, attr, raw_val)
                else:
                    target_full = f"{base}/{on_fail}" if base else on_fail
                    em.put(target_full, raw_val)
                return
            if error_policy == "fail":
                raise
            return

        # attributes first
        for k, v in attrs.items():
            if isinstance(v, str) and v.startswith("$mt."):
                v = get_value(mt, v[4:])
            target_full = f"{base}/{target}" if base else target
            em.put_attr(target_full, k, v)

        # main value
        if "/@" in target:
            parent, attr = target.split("/@")
            parent_full = f"{base}/{parent}" if base else parent
            em.put_attr(parent_full, attr, out_val)
        else:
            target_full = f"{base}/{target}" if base else target
            em.put(target_full, out_val)

    # process blocks; each block can have its own sub-root (e.g., CdtTrfTxInf)
    for block in mapping.get("blocks", []):
        base = block.get("target_root", "") or ""
        for m in block.get("mappings", []):
            if "switch" in m:
                when_any = m.get("when_any") or []
                present = any(get_value(mt, w.get("exists","")) is not None for w in when_any) if when_any else True
                #if when_any and not any(get_value(mt, w.get("exists","")) is not None for w in when_any):
                #    continue
                fired = False
                for br in m.get("switch", []):
                    cond = br.get("if", {})
                    if get_value(mt, cond.get("exists","")) is not None:
                        for mm in br.get("mappings", []):
                            _emit_simple(mm, base)
                        fired = True
                        break
                if not fired:
                    for mm in (m.get("default") or []):
                        _emit_simple(mm, base)
                    continue
                 #   pass
            else:
                _emit_simple(m, base)

    # validations (respect full path; so include base in mapping where needed)
    for val in mapping.get("validations", []):
        if val.get("required"):
            rel = val["path"]
            full = f"/Document/{mx_root}/{rel}" if rel else f"/Document/{mx_root}"
            ok = full in em.flat and any(v not in ("", None) for v in em.flat[full])
            if not ok:
                parent = "/".join(full.split("/")[:-1])
                nearby = sorted([k for k in em.flat.keys() if k.startswith(parent)])
                raise ValueError(
                    "Validation failed: required path missing\n"
                    f"  required : {rel}\n"
                    f"  looked at: {full}\n"
                    f"  nearby   : {nearby[:10]}{' ...' if len(nearby) > 10 else ''}"
                )
                raise ValueError(f"Validation failed: required '{rel}' missing")

    return em.flat

# ---------- Tiny compatibility wrapper for routes.py ----------

class Transformer:
    """
    Thin adapter so routes.py can keep using:
        transformer = Transformer(xsd_index=None)
        flat, audit_details = transformer.apply(mapping, parsed)
    """
    def __init__(self, xsd_index=None, mx_root: str = "FIToFICstmrCdtTrf"):
        self.xsd_index = xsd_index
        self.mx_root = mx_root

    def apply(self, mapping: dict, parsed: dict):
        mt_fields = parsed.get("fields", parsed)
        context = {}
        meta = parsed.get("meta") if isinstance(parsed, dict) else None
        if isinstance(meta, dict) and "request_id" in meta:
            context["request_id"] = meta["request_id"]

        errors = []
        flat = {}
        mx_root = mapping.get("meta", {}).get("mx_root") or mapping.get("mx_root") or self.mx_root
        try:
            flat = apply_mapping_flat(mt_fields, mapping, context=context, mx_root=mx_root)
        except Exception as e:
            errors.append(str(e))
            raise
        finally:
            mapped = sorted(list(flat.keys())) if flat else []

        audit_details = { "mapped": mapped, "errors": errors }
        return flat, audit_details
