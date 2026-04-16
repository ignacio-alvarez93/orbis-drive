from __future__ import annotations

from typing import Any


def _round_value(value: float, digits: int = 1) -> float:
    return round(float(value), digits)


def derive_power_to_weight_cv_ton(data: dict[str, Any], result) -> None:
    power_cv = data.get("power_cv") or data.get("max_power_cv")
    kerb_weight_kg = data.get("kerb_weight_kg")

    if power_cv in (None, "") or kerb_weight_kg in (None, "", 0):
        return

    tons = float(kerb_weight_kg) / 1000.0
    if tons == 0:
        return

    result.add_field(
        field_name="power_to_weight_cv_ton",
        value=_round_value(float(power_cv) / tons, 1),
        source="power_cv + kerb_weight_kg",
        rule="weight_rules.derive_power_to_weight_cv_ton",
        confidence="deterministic",
    )


def derive_power_to_weight_kw_ton(data: dict[str, Any], result) -> None:
    kerb_weight_kg = data.get("kerb_weight_kg")
    power_kw = result.enriched_fields.get("max_power_kw") or data.get("max_power_kw")

    if power_kw in (None, "") or kerb_weight_kg in (None, "", 0):
        return

    tons = float(kerb_weight_kg) / 1000.0
    if tons == 0:
        return

    result.add_field(
        field_name="power_to_weight_kw_ton",
        value=_round_value(float(power_kw) / tons, 1),
        source="max_power_kw + kerb_weight_kg",
        rule="weight_rules.derive_power_to_weight_kw_ton",
        confidence="deterministic",
    )
