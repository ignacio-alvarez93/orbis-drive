from __future__ import annotations

from typing import Any

# Fórmulas estándar:
# mpg_uk = 282.481 / (L/100km)
# mpg_us = 235.215 / (L/100km)

MPG_UK_FACTOR = 282.481
MPG_US_FACTOR = 235.215


def _round_value(value: float, digits: int = 1) -> float:
    return round(float(value), digits)


def derive_fuel_consumption_combined_mpg_uk(data: dict[str, Any], result) -> None:
    l_100km = data.get("fuel_consumption_combined_l_100km")
    if l_100km in (None, "", 0):
        return

    result.add_field(
        field_name="fuel_consumption_combined_mpg_uk",
        value=_round_value(MPG_UK_FACTOR / float(l_100km), 1),
        source="fuel_consumption_combined_l_100km",
        rule="efficiency_rules.derive_fuel_consumption_combined_mpg_uk",
        confidence="deterministic",
    )


def derive_fuel_consumption_combined_mpg_us(data: dict[str, Any], result) -> None:
    l_100km = data.get("fuel_consumption_combined_l_100km")
    if l_100km in (None, "", 0):
        return

    result.add_field(
        field_name="fuel_consumption_combined_mpg_us",
        value=_round_value(MPG_US_FACTOR / float(l_100km), 1),
        source="fuel_consumption_combined_l_100km",
        rule="efficiency_rules.derive_fuel_consumption_combined_mpg_us",
        confidence="deterministic",
    )
