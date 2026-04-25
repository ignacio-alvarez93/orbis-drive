import hashlib
from typing import Optional

from ..models.concesionario_validated import ConcesionarioValidated


def _safe(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def build_semantic_key(
    validated: ConcesionarioValidated,
    localidad_id: Optional[int],
) -> Optional[str]:
    normalized = validated.normalized

    nombre = _safe(normalized.nombre_canonical)
    direccion = _safe(normalized.direccion_texto_normalizada)
    cp = _safe(normalized.codigo_postal_normalizado)
    domain = _safe(normalized.website_domain)

    if not nombre:
        return None

    if localidad_id and direccion:
        return f"{nombre}|loc:{localidad_id}|dir:{direccion}"

    if localidad_id and (cp or domain):
        return f"{nombre}|loc:{localidad_id}|cp:{cp}|dom:{domain}"

    return None


def build_concesionario_id(semantic_key: Optional[str]) -> Optional[str]:
    if not semantic_key:
        return None

    return hashlib.sha1(semantic_key.encode("utf-8")).hexdigest()