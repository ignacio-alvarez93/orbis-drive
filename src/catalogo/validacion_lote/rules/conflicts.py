from __future__ import annotations

from collections import defaultdict
from typing import Any

from ..lote_result import ValidationIssue
from src.catalogo.validacion_lote.rules.semantic_key_v2 import (
    build_conflict_key,
    build_semantic_key_v2,
)

HARD_CONFLICT_FIELDS = (
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


def group_by_conflict_key(records: list[dict[str, Any]]) -> dict[str, list[tuple[int, dict[str, Any]]]]:
    grouped: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for idx, record in enumerate(records):
        grouped[build_conflict_key(record)].append((idx, record))
    return dict(grouped)


def detect_group_conflicts(records: list[dict[str, Any]]):
    """
    Detecta contradicciones entre registros que pretenden describir la misma versión base
    dentro del mismo marco temporal explícito, o sin diferenciación temporal suficiente.
    """
    issues: list[ValidationIssue] = []
    grouped = group_by_conflict_key(records)

    for conflict_key, members in grouped.items():
        if len(members) <= 1:
            continue

        for field in HARD_CONFLICT_FIELDS:
            values: dict[Any, list[int]] = {}

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
                        semantic_key=conflict_key,
                        generation_key="|".join(conflict_key.split("|")[:3]),
                        record_indexes=sorted(idx for indexes in values.values() for idx in indexes),
                        fields=[field],
                        details={"values": values},
                    )
                )

    return issues


def detect_internal_record_conflicts(records):
    issues: list[ValidationIssue] = []

    for idx, record in enumerate(records):
        semantic_key = build_semantic_key_v2(record)

        cc = record.get("engine_displacement_cc")
        liters = record.get("engine_displacement_l")

        if cc is not None and liters is not None:
            try:
                expected_cc = float(liters) * 1000
                if abs(float(cc) - expected_cc) > 150:
                    issues.append(
                        ValidationIssue(
                            code="conflict_displacement_l_vs_cc",
                            severity="error",
                            message="Cilindrada incoherente entre litros y cc.",
                            semantic_key=semantic_key,
                            generation_key="|".join(semantic_key.split("|")[:3]),
                            record_indexes=[idx],
                            fields=["engine_displacement_l", "engine_displacement_cc"],
                        )
                    )
            except Exception:
                pass

    return issues
