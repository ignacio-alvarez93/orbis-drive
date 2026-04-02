from __future__ import annotations

import re
from typing import Any, Dict, List

from src.catalogo.dvl.enums.fuel_type import normalize_fuel_type
from src.catalogo.dvl.enums.gearbox_type import normalize_gearbox_type

CRITICAL_IDENTITY_FIELDS = (
    "manufacturer_name",
    "model_name",
    "version_name",
    "fuel_type",
)

STRING_FIELDS_TO_TRIM = (
    "manufacturer_name",
    "model_name",
    "generation_name",
    "version_name",
    "body_type",
    "fuel_type",
    "gearbox_type",
    "drive_type",
)

BODY_TYPE_ALIASES = {
    "hatchback": "hatchback",
    "pequeño hatchback": "hatchback",
    "small hatchback": "hatchback",
    "sedan": "sedan",
    "berlina": "sedan",
    "estate": "estate",
    "wagon": "estate",
    "familiar": "estate",
    "suv": "suv",
    "coupe": "coupe",
    "coupé": "coupe",
    "cabrio": "cabrio",
    "cabriolet": "cabrio",
    "roadster": "roadster",
    "mpv": "mpv",
    "monovolumen": "mpv",
    "van": "van",
    "pickup": "pickup",
}

DRIVE_TYPE_ALIASES = {
    "fwd": "fwd",
    "front wheel drive": "fwd",
    "rwd": "rwd",
    "rear wheel drive": "rwd",
    "awd": "awd",
    "all wheel drive": "awd",
    "4wd": "4wd",
    "4x4": "4wd",
    "four wheel drive": "4wd",
}


def normalize_identity_fields(record: Dict[str, Any]) -> None:
    for field in STRING_FIELDS_TO_TRIM:
        value = record.get(field)
        if isinstance(value, str):
            cleaned = _clean_text(value)
            record[field] = cleaned if cleaned else None

    for field in ("manufacturer_name", "model_name", "generation_name", "version_name"):
        value = record.get(field)
        if isinstance(value, str):
            record[field] = value.upper()

    record["fuel_type"] = normalize_fuel_type(record.get("fuel_type"))
    record["gearbox_type"] = normalize_gearbox_type(record.get("gearbox_type"))

    body_type = record.get("body_type")
    if isinstance(body_type, str):
        candidate = " ".join(body_type.strip().lower().split())
        record["body_type"] = BODY_TYPE_ALIASES.get(candidate, candidate)
    elif body_type is not None:
        record["body_type"] = None

    drive_type = record.get("drive_type")
    if isinstance(drive_type, str):
        candidate = " ".join(drive_type.strip().lower().split())
        record["drive_type"] = DRIVE_TYPE_ALIASES.get(candidate, candidate)
    elif drive_type is not None:
        record["drive_type"] = None


def validate_identity_rules(record: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
    for field in CRITICAL_IDENTITY_FIELDS:
        if record.get(field) is None:
            errors.append(f"{field}: campo crítico ausente o inválido")

    for field in ("manufacturer_name", "model_name", "version_name"):
        value = record.get(field)
        if value is not None and not isinstance(value, str):
            errors.append(f"{field}: debe ser string")

    generation_name = record.get("generation_name")
    if generation_name is not None and not isinstance(generation_name, str):
        warnings.append("generation_name: valor no string")

    body_type = record.get("body_type")
    if body_type is not None and not isinstance(body_type, str):
        warnings.append("body_type: valor no string → NULL")
        record["body_type"] = None


def _clean_text(value: str) -> str:
    value = value.strip()
    value = value.replace("\u00A0", " ")
    value = re.sub(r"[\t\r\n]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[^\w\s\-/().,+]", "", value, flags=re.UNICODE)
    return value.strip()
