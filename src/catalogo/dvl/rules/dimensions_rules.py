from __future__ import annotations

from typing import Any, Dict, List, Optional


def normalize_dimensions_fields(record: Dict[str, Any]) -> None:
    doors = record.get("doors")
    if isinstance(doors, str):
        stripped = doors.strip()
        if stripped.isdigit():
            record["doors"] = int(stripped)
        else:
            record["doors"] = stripped

    seats = record.get("seats")
    if isinstance(seats, str):
        stripped = seats.strip()
        if stripped.isdigit():
            record["seats"] = int(stripped)


def validate_dimensions_rules(record: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
    doors = record.get("doors")
    seats = _to_float(record.get("seats"))
    boot_capacity_l = _to_float(record.get("boot_capacity_l"))
    boot_capacity_min_l = _to_float(record.get("boot_capacity_min_l"))
    boot_capacity_max_l = _to_float(record.get("boot_capacity_max_l"))

    if doors is not None:
        if isinstance(doors, int):
            if doors <= 0:
                warnings.append("doors: valor no positivo")
            elif doors > 8:
                warnings.append("doors: sospechosamente alto")
        elif isinstance(doors, str):
            pass
        else:
            warnings.append("doors: tipo inválido")

    if seats is not None:
        if seats <= 0:
            warnings.append("seats: valor no positivo")
        elif seats > 12:
            warnings.append("seats: sospechosamente alto")

    if boot_capacity_l is not None:
        if boot_capacity_l <= 0:
            warnings.append("boot_capacity_l: valor no positivo o absurdo")
        elif boot_capacity_l < 20:
            warnings.append("boot_capacity_l: sospechosamente bajo")

    if boot_capacity_min_l is not None:
        if boot_capacity_min_l <= 0:
            warnings.append("boot_capacity_min_l: valor no positivo o absurdo")
        elif boot_capacity_min_l < 20:
            warnings.append("boot_capacity_min_l: sospechosamente bajo")

    if boot_capacity_max_l is not None:
        if boot_capacity_max_l <= 0:
            warnings.append("boot_capacity_max_l: valor no positivo o absurdo")
        elif boot_capacity_max_l < 20:
            warnings.append("boot_capacity_max_l: sospechosamente bajo")

    if boot_capacity_min_l is not None and boot_capacity_max_l is not None and boot_capacity_min_l > boot_capacity_max_l:
        warnings.append("maletero incoherente: min_l > max_l")


def _to_float(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None
