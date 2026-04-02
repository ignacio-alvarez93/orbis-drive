from __future__ import annotations

from typing import Optional

FUEL_TYPE_ALIASES = {
    "gasoline": "gasoline",
    "petrol": "gasoline",
    "gasolina": "gasoline",
    "diesel": "diesel",
    "diésel": "diesel",
    "gasoil": "diesel",
    "mhev": "mhev",
    "mild hybrid": "mhev",
    "hev": "hev",
    "hybrid": "hev",
    "full hybrid": "hev",
    "phev": "phev",
    "plug-in hybrid": "phev",
    "plugin hybrid": "phev",
    "ev": "ev",
    "electric": "ev",
    "bev": "ev",
    "lpg": "lpg",
    "glp": "lpg",
    "cng": "cng",
    "gnc": "cng",
    "hydrogen": "hydrogen",
    "h2": "hydrogen",
    "flex fuel": "flex_fuel",
    "flexfuel": "flex_fuel",
    "ethanol": "flex_fuel",
}

ALLOWED_FUEL_TYPES = set(FUEL_TYPE_ALIASES.values())


def normalize_fuel_type(value: object) -> Optional[str]:
    if value is None or not isinstance(value, str):
        return None
    candidate = " ".join(value.strip().lower().split())
    return FUEL_TYPE_ALIASES.get(candidate)
