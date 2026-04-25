from dataclasses import dataclass
from typing import List
from .concesionario_normalized import ConcesionarioNormalized


@dataclass
class ConcesionarioValidated:
    normalized: ConcesionarioNormalized

    is_valid: bool

    validation_errors: List[str]
    validation_warnings: List[str]

    classification_status: str  # INGESTABLE / PENDIENTE / RECHAZADO