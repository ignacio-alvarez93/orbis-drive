from __future__ import annotations

from typing import Any

CV_TO_KW = 0.73549875
KMH_TO_MPH = 0.621371


def _round_value(value: float, digits: int = 1) -> float:
    return round(float(value), digits)


def derive_max_power_kw(data: dict[str, Any], result) -> None:
    power_cv = data.get("max_power_cv") or data.get("power_cv")
    if power_cv in (None, ""):
        return

    result.add_field(
        field_name="max_power_kw",
        value=_round_value(float(power_cv) * CV_TO_KW, 1),
        source="max_power_cv" if data.get("max_power_cv") not in (None, "") else "power_cv",
        rule="performance_conversion_rules.derive_max_power_kw",
        confidence="deterministic",
    )


def derive_specific_output_kw_l(data: dict[str, Any], result) -> None:
    displacement_l = data.get("engine_displacement_l")
    power_kw = (
        result.enriched_fields.get("max_power_kw")
        or data.get("max_power_kw")
    )

    if displacement_l in (None, "", 0) or power_kw in (None, ""):
        return

    result.add_field(
        field_name="specific_output_kw_l",
        value=_round_value(float(power_kw) / float(displacement_l), 1),
        source="max_power_kw + engine_displacement_l",
        rule="performance_conversion_rules.derive_specific_output_kw_l",
        confidence="deterministic",
    )


def derive_top_speed_mph(data: dict[str, Any], result) -> None:
    top_speed_kmh = data.get("top_speed_kmh")
    if top_speed_kmh in (None, ""):
        return

    result.add_field(
        field_name="top_speed_mph",
        value=_round_value(float(top_speed_kmh) * KMH_TO_MPH, 1),
        source="top_speed_kmh",
        rule="performance_conversion_rules.derive_top_speed_mph",
        confidence="deterministic",
    )
