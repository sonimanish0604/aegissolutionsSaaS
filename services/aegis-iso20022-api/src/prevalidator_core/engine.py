from __future__ import annotations

from typing import Dict, List, Optional

from ..translator_core.detector import Detector
from ..translator_core.mt_parser import MTParser

from .loader import FieldDefinitionsLoader
from .models import ValidationError, ValidationResult
from .rules import apply_rule


class PrevalidationEngine:
    def __init__(self) -> None:
        self.loader = FieldDefinitionsLoader()
        self.detector = Detector()
        self.parser = MTParser()

    def _detect_type(self, raw: str, force_type: Optional[str]) -> Optional[str]:
        if force_type:
            return force_type.upper()
        return self.detector.detect(raw)

    def validate(self, raw: str, force_type: Optional[str] = None) -> ValidationResult:
        mt_type = self._detect_type(raw, force_type)
        if not mt_type:
            return ValidationResult(mt_type="UNKNOWN", valid=False, errors=[ValidationError(field="__message__", message="Unable to detect MT type")])

        definitions = self.loader.get_definitions(mt_type)
        if definitions is None:
            return ValidationResult(mt_type=mt_type, valid=False, errors=[ValidationError(field="__message__", message=f"No field validations defined for {mt_type}")])

        parsed = self.parser.parse(mt_type, raw)
        fields: Dict[str, List[str]] = parsed.get("fields", {})  # type: ignore

        errors: List[ValidationError] = []

        def get_field_values(tag: str) -> List[str]:
            if not tag:
                return []
            upper_tag = tag.upper()
            if upper_tag in fields:
                return fields[upper_tag]
            if tag in fields:
                return fields[tag]
            if len(tag) > 2 and tag[-1].isalpha() and tag[-1].islower():
                base = tag[:-1]
                if base in fields:
                    return fields[base]
                if base.upper() in fields:
                    return fields[base.upper()]
                # Handle optioned fields (e.g. 59a -> 59A, 59F, etc.).
                prefix = base.upper()
                collected: List[str] = []
                for key, vals in fields.items():
                    upper_key = key.upper()
                    if upper_key == prefix or (upper_key.startswith(prefix) and len(upper_key) == len(prefix) + 1 and upper_key[-1].isalpha()):
                        collected.extend(vals)
                if collected:
                    return collected
            return []

        # Presence checks
        for field_def in definitions:
            tag = field_def.get("tag")
            presence = field_def.get("presence")
            if not tag or not presence:
                continue
            values = get_field_values(tag)
            if presence == "mandatory" and (not values or all(v.strip() == "" for v in values)):
                errors.append(ValidationError(field=tag, message="Field is mandatory but missing", code="PRESENCE"))

        # Value validations
        for field_def in definitions:
            tag = field_def.get("tag")
            if not tag:
                continue
            validations = field_def.get("validations") or []
            if not validations:
                continue
            values = get_field_values(tag)
            for idx, value in enumerate(values, start=1):
                for validation in validations:
                    rule_name = validation.get("rule") if isinstance(validation, dict) else None
                    error_code = validation.get("error_code") if isinstance(validation, dict) else None
                    if not rule_name:
                        continue
                    error_message = apply_rule(rule_name, value)
                    if error_message:
                        errors.append(ValidationError(field=tag, message=error_message, code=error_code, occurrence=idx))

        return ValidationResult(mt_type=mt_type, valid=not errors, errors=errors)
