from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationError:
    field: str
    message: str
    code: Optional[str] = None
    sequence: Optional[str] = None
    occurrence: Optional[int] = None

    def to_dict(self) -> dict:
        data = {
            "field": self.field,
            "message": self.message,
        }
        if self.code:
            data["code"] = self.code
        if self.sequence:
            data["sequence"] = self.sequence
        if self.occurrence is not None:
            data["occurrence"] = self.occurrence
        return data


@dataclass
class ValidationResult:
    mt_type: str
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "mt_type": self.mt_type,
            "valid": self.valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
        }
