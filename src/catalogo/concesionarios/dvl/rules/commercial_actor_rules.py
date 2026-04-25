from typing import List

from ...models.concesionario_normalized import ConcesionarioNormalized


DISALLOWED_TYPES = {
    "particular",
}

WEAK_NON_COMMERCIAL_NAMES = {
    "juan perez",
    "maria garcia",
    "jose lopez",
}


def validate_commercial_actor(normalized: ConcesionarioNormalized) -> List[str]:
    errors: List[str] = []

    dealer_type = (normalized.tipo_concesionario_normalizado or "").strip().lower()
    canonical_name = (normalized.nombre_canonical or "").strip().lower()

    if dealer_type in DISALLOWED_TYPES:
        errors.append("dealer_type indica actor no comercial")

    if canonical_name in WEAK_NON_COMMERCIAL_NAMES:
        errors.append("nombre compatible con particular no identificado como profesional")

    has_minimum_signal = any([
        normalized.raw.address_raw,
        normalized.raw.location_raw,
        normalized.raw.phone_raw,
        normalized.raw.website_raw,
        normalized.raw.description_raw,
    ])

    if not has_minimum_signal:
        errors.append("registro sin señales minimas de actor comercial")

    return errors