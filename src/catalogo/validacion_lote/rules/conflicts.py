from __future__ import annotations

from typing import Any

from ..lote_result import ValidationIssue

CRITICAL_FIELDS = (
    "power_cv",
    "max_power_cv",
    "fuel_type",
    "gearbox_type",
    "gear_count",
    "engine_displacement_l",
    "engine_displacement_cc",
    "max_torque_nm",
    "drive_type",
)


def _normalize_scalar(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        value = " ".join(value.strip().upper().split())
        return value or None
    if isinstance(value, float):
        return round(value, 4)
    return value


def detect_group_conflicts(grouped_records: dict[str, list[tuple[int, dict[str, Any]]]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for semantic_key, members in grouped_records.items():
        if len(members) <= 1:
            continue
        for field in CRITICAL_FIELDS:
            values = {}
            for idx, record in members:
                value = _normalize_scalar(record.get(field))
                if value is None:
                    continue
                values.setdefault(value, []).append(idx)
            if len(values) > 1:
                issues.append(
                    ValidationIssue(
                        code="conflict_same_version",
                        severity="error",
                        message=f"La versión presenta conflicto interno en el campo '{field}'.",
                        semantic_key=semantic_key,
                        generation_key="|".join(semantic_key.split("|")[:3]),
                        record_indexes=sorted(idx for indexes in values.values() for idx in indexes),
                        fields=[field],
                        details={"values": values},
                    )
                )
    return issues


def detect_internal_record_conflicts(records: list[dict[str, Any]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for idx, record in enumerate(records):
        semantic_key = "|".join(
            " ".join(str(record.get(k, "")).strip().upper().split())
            for k in ("manufacturer_name", "model_name", "generation_name", "version_name")
        )

        cc = record.get("engine_displacement_cc")
        liters = record.get("engine_displacement_l")
        if cc is not None and liters is not None:
            try:
                expected_cc = float(liters) * 1000
                delta = abs(float(cc) - expected_cc)
                if delta > 150:
                    issues.append(
                        ValidationIssue(
                            code="conflict_displacement_l_vs_cc",
                            severity="error",
                            message="Cilindrada en litros y en cc no son coherentes dentro del mismo registro.",
                            semantic_key=semantic_key,
                            generation_key="|".join(semantic_key.split("|")[:3]),
                            record_indexes=[idx],
                            fields=["engine_displacement_l", "engine_displacement_cc"],
                            details={"engine_displacement_l": liters, "engine_displacement_cc": cc},
                        )
                    )
            except (TypeError, ValueError):
                pass

        power = record.get("power_cv")
        max_power = record.get("max_power_cv")
        if power is not None and max_power is not None:
            try:
                if abs(float(power) - float(max_power)) > 5:
                    issues.append(
                        ValidationIssue(
                            code="conflict_power_vs_max_power",
                            severity="error",
                            message="power_cv y max_power_cv no son coherentes dentro del mismo registro.",
                            semantic_key=semantic_key,
                            generation_key="|".join(semantic_key.split("|")[:3]),
                            record_indexes=[idx],
                            fields=["power_cv", "max_power_cv"],
                            details={"power_cv": power, "max_power_cv": max_power},
                        )
                    )
            except (TypeError, ValueError):
                pass
    return issues
