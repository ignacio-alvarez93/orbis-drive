from dataclasses import dataclass
from typing import Optional
from .concesionario_validated import ConcesionarioValidated


@dataclass
class ConcesionarioResolved:
    validated: ConcesionarioValidated

    pais_id: Optional[int]
    subdivision_id: Optional[int]
    localidad_id: Optional[int]

    semantic_key_concesionario: Optional[str]
    concesionario_id: Optional[str]