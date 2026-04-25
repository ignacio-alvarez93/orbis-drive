from dataclasses import dataclass
from typing import Optional, List
from .concesionario_raw_record import ConcesionarioRawRecord


@dataclass
class ConcesionarioNormalized:
    raw: ConcesionarioRawRecord

    nombre_canonical: str

    direccion_texto_normalizada: Optional[str]
    codigo_postal_normalizado: Optional[str]

    website_domain: Optional[str]

    tipo_concesionario_normalizado: Optional[str]

    location_candidates: List[str]