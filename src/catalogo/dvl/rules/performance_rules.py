from __future__ import annotations

from typing import Any, Dict, List, Optional


def validate_performance_rules(record: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
    power_cv = _to_float(record.get("power_cv"))
    power_kw = _to_float(record.get("power_kw") or record.get("max_power_kw"))
    max_power_cv = _to_float(record.get("max_power_cv"))
    top_speed_kmh = _to_float(record.get("top_speed_kmh"))
    top_speed_mph = _to_float(record.get("top_speed_mph"))
    gearbox_type = record.get("gearbox_type")
    gear_count = _to_float(record.get("gear_count") or record.get("gearbox_gears"))

    if record.get("power_cv") is not None:
        if power_cv is None:
            warnings.append("power_cv: tipo inválido")
        elif power_cv <= 0:
            warnings.append("power_cv: valor no positivo")

    if record.get("max_power_cv") is not None:
        if max_power_cv is None:
            warnings.append("max_power_cv: tipo inválido")
        elif max_power_cv <= 0:
            warnings.append("max_power_cv: valor no positivo")

    if power_cv is not None and max_power_cv is not None:
        if abs(power_cv - max_power_cv) > max(3.0, max_power_cv * 0.03):
            warnings.append("power_cv incoherente con max_power_cv")

    if power_cv is not None and power_kw is not None:
        expected_kw = power_cv * 0.73549875
        if abs(power_kw - expected_kw) > max(2.0, expected_kw * 0.05):
            warnings.append("potencia incoherente entre CV y kW")

    if top_speed_kmh is not None:
        if top_speed_kmh <= 0:
            warnings.append("top_speed_kmh: valor no positivo")
        elif top_speed_kmh < 40:
            warnings.append("top_speed_kmh: sospechosamente bajo")
        elif top_speed_kmh > 450:
            warnings.append("top_speed_kmh: sospechosamente alto")

    if top_speed_kmh is not None and top_speed_mph is not None:
        expected_mph = top_speed_kmh * 0.621371
        if abs(top_speed_mph - expected_mph) > max(3.0, expected_mph * 0.05):
            warnings.append("top_speed_mph incoherente con top_speed_kmh")

    if gear_count is not None and gearbox_type is None:
        warnings.append("gear_count presente sin gearbox_type")
    if gearbox_type is not None and gear_count is None:
        warnings.append("gearbox_type presente sin gear_count")
    if gear_count is not None and (gear_count <= 0 or gear_count > 12):
        warnings.append("gear_count: valor fuera de rango razonable")


def _to_float(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None
