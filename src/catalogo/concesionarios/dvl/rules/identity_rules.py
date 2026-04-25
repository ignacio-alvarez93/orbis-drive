from typing import List

from ...models.concesionario_normalized import ConcesionarioNormalized


GENERIC_BAD_NAMES = {
    "profesional",
    "concesionario",
    "compraventa",
    "vehiculos",
    "vehiculos ocasion",
    "coches",
    "coches de ocasion",
    "autos",
    "motor",
    "automocion",
    "automoviles",
    "taller",
    "particular",
    "anuncio",
}

NON_COMMERCIAL_PERSON_PATTERNS = {
    "juan",
    "maria",
    "jose",
    "garcia",
    "perez",
    "lopez",
    "martinez",
}


def validate_identity(normalized: ConcesionarioNormalized) -> List[str]:
    errors: List[str] = []

    raw_name = normalized.raw.dealer_name_raw or ""
    canonical_name = normalized.nombre_canonical or ""

    if not raw_name.strip():
        errors.append("dealer_name_raw vacio")
        return errors

    if len(canonical_name) < 3:
        errors.append("nombre_canonical demasiado corto")

    if canonical_name in GENERIC_BAD_NAMES:
        errors.append("nombre demasiado generico para identificar actor comercial")

    tokens = canonical_name.split()
    if len(tokens) == 1 and canonical_name in {"profesional", "concesionario", "motor"}:
        errors.append("nombre insuficiente para identidad comercial")

    if len(tokens) <= 2 and all(token in NON_COMMERCIAL_PERSON_PATTERNS for token in tokens):
        errors.append("nombre parece persona fisica no identificada como actor comercial")

    if not normalized.raw.location_raw.strip():
        errors.append("location_raw vacio")

    return errors