from typing import Any


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().upper().split())


def _has_explicit_period(record: dict[str, Any]) -> bool:
    return bool(record.get("production_start_year") or record.get("production_end_year"))


def build_generation_key(record: dict[str, Any]) -> str:
    return "|".join([
        normalize_text(record.get("manufacturer_name")),
        normalize_text(record.get("model_name")),
        normalize_text(record.get("generation_name")),
    ])


def build_base_version_key(record: dict[str, Any]) -> str:
    """
    Identidad comercial base.
    Sirve para razonar sobre 'misma versión declarada' sin mezclar aún dimensión técnica.
    """
    return "|".join([
        normalize_text(record.get("manufacturer_name")),
        normalize_text(record.get("model_name")),
        normalize_text(record.get("generation_name")),
        normalize_text(record.get("version_name")),
    ])


def build_conflict_key(record: dict[str, Any]) -> str:
    """
    Clave de agrupación para detectar contradicciones.
    - Si hay periodo explícito, se compara dentro del mismo marco temporal.
    - Si no hay periodo, se agrupa por identidad base y se exige consistencia.
    """
    parts = [build_base_version_key(record)]
    if _has_explicit_period(record):
        parts.extend([
            normalize_text(record.get("production_start_year")),
            normalize_text(record.get("production_end_year")),
        ])
    return "|".join(parts)


def build_variant_key(record: dict[str, Any]) -> str:
    """
    Identidad semántica oficial de variante.
    Definición aprobada:
      manufacturer + model + generation + version_name + production years
    Fallback controlado:
      + power_cv + fuel_type
    """
    base = [
        normalize_text(record.get("manufacturer_name")),
        normalize_text(record.get("model_name")),
        normalize_text(record.get("generation_name")),
        normalize_text(record.get("version_name")),
        normalize_text(record.get("production_start_year")),
        normalize_text(record.get("production_end_year")),
    ]

    if not _has_explicit_period(record):
        base.extend([
            normalize_text(record.get("power_cv")),
            normalize_text(record.get("fuel_type")),
        ])

    return "|".join(base)


def build_duplicate_key(record: dict[str, Any]) -> str:
    """
    Para duplicados usamos la misma identidad semántica completa.
    """
    return build_variant_key(record)


def build_semantic_key_v2(record: dict[str, Any]) -> str:
    """
    Alias de compatibilidad.
    """
    return build_variant_key(record)
