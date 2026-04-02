from __future__ import annotations

from typing import Optional

GEARBOX_TYPE_ALIASES = {
    "manual": "manual",
    "mt": "manual",
    "automatic": "automatic",
    "auto": "automatic",
    "at": "automatic",
    "automatica": "automatic",
    "automática": "automatic",
    "cvt": "cvt",
    "dct": "dct",
    "dsg": "dct",
    "semi automatic": "semi_automatic",
    "semi-automatic": "semi_automatic",
    "reduction gear": "reduction_gear",
    "single speed": "reduction_gear",
}

ALLOWED_GEARBOX_TYPES = set(GEARBOX_TYPE_ALIASES.values())


def normalize_gearbox_type(value: object) -> Optional[str]:
    if value is None or not isinstance(value, str):
        return None
    candidate = " ".join(value.strip().lower().split())
    return GEARBOX_TYPE_ALIASES.get(candidate)
