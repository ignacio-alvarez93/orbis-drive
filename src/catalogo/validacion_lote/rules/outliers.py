from __future__ import annotations

from typing import Any

from ..lote_result import ValidationIssue


RANGES = {
    "boot_capacity_max_l": (50, 3000),
    "boot_capacity_min_l": (50, 3000),
    "top_speed_kmh": (60, 450),
    "acceleration_0_100_s": (2, 60),
    "fuel_consumption_combined_l_100km": (1.5, 40),
    "max_power_rpm": (1500, 12000),
    "max_torque_rpm": (500, 9000),
    "engine_displacement_cc": (250, 10000),
    "engine_displacement_l": (0.2, 10),
}


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def detect_outliers(records: list[dict[str, Any]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for idx, record in enumerate(records):
        semantic_key = "|".join(
            " ".join(str(record.get(k, "")).strip().upper().split())
            for k in ("manufacturer_name", "model_name", "generation_name", "version_name")
        )
        for field, (low, high) in RANGES.items():
            value = _to_float(record.get(field))
            if value is None:
                continue
            if value < low or value > high:
                issues.append(
                    ValidationIssue(
                        code="outlier_value",
                        severity="warning",
                        message=f"Valor fuera de rango lógico en '{field}'.",
                        semantic_key=semantic_key,
                        generation_key="|".join(semantic_key.split("|")[:3]),
                        record_indexes=[idx],
                        fields=[field],
                        details={"value": value, "expected_range": [low, high]},
                    )
                )

        min_boot = _to_float(record.get("boot_capacity_min_l"))
        max_boot = _to_float(record.get("boot_capacity_max_l"))
        if min_boot is not None and max_boot is not None and max_boot < min_boot:
            issues.append(
                ValidationIssue(
                    code="outlier_boot_range",
                    severity="warning",
                    message="boot_capacity_max_l es menor que boot_capacity_min_l.",
                    semantic_key=semantic_key,
                    generation_key="|".join(semantic_key.split("|")[:3]),
                    record_indexes=[idx],
                    fields=["boot_capacity_min_l", "boot_capacity_max_l"],
                    details={"boot_capacity_min_l": min_boot, "boot_capacity_max_l": max_boot},
                )
            )
    return issues
