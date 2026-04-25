from dataclasses import dataclass, field
from typing import Dict, List

from ..models.concesionario_resolved import ConcesionarioResolved
from .rules.duplicates import detect_duplicates
from .rules.conflicts import detect_conflicts


@dataclass
class ValidacionLoteResult:
    is_valid_dataset: bool
    duplicates: Dict[str, List[ConcesionarioResolved]] = field(default_factory=dict)
    duplicate_warnings: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)


class ValidacionLoteConcesionarios:

    @classmethod
    def validate(cls, records: List[ConcesionarioResolved]) -> ValidacionLoteResult:
        duplicates, duplicate_warnings = detect_duplicates(records)
        conflicts = detect_conflicts(records)

        is_valid_dataset = len(conflicts) == 0

        return ValidacionLoteResult(
            is_valid_dataset=is_valid_dataset,
            duplicates=duplicates,
            duplicate_warnings=duplicate_warnings,
            conflicts=conflicts,
        )