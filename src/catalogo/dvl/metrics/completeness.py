from __future__ import annotations

from typing import Any, Dict, List

CRITICAL_FIELDS = {
    "manufacturer_name",
    "model_name",
    "version_name",
    "fuel_type",
}

RELEVANT_FIELDS = {
    "body_type",
    "drive_type",
    "gearbox_type",
    "power_cv",
    "max_power_cv",
    "engine_displacement_l",
    "production_start_year",
    "production_end_year",
}

INFORMATIVE_FIELDS = {
    "max_power_rpm",
    "max_torque_nm",
    "max_torque_rpm",
    "gear_count",
    "doors",
    "seats",
    "boot_capacity_l",
    "boot_capacity_min_l",
    "boot_capacity_max_l",
    "length_mm",
    "width_mm",
    "height_mm",
    "wheelbase_mm",
}


def _is_present(value: Any) -> bool:
    return value is not None


def build_completeness_metrics(
    record: Dict[str, Any],
    errors: List[str],
    warnings: List[str],
) -> Dict[str, Any]:
    total_fields = len(record)
    present_fields = sum(1 for value in record.values() if _is_present(value))
    completeness_score = present_fields / total_fields if total_fields else 0.0

    critical_ok = sum(1 for field in CRITICAL_FIELDS if _is_present(record.get(field)))
    relevant_ok = sum(1 for field in RELEVANT_FIELDS if _is_present(record.get(field)))
    informative_ok = sum(1 for field in INFORMATIVE_FIELDS if _is_present(record.get(field)))

    return {
        "total_fields": total_fields,
        "present_fields": present_fields,
        "missing_fields": total_fields - present_fields,
        "completeness_score": round(completeness_score, 4),
        "critical_fields_total": len(CRITICAL_FIELDS),
        "critical_fields_ok": critical_ok,
        "critical_ok_ratio": round(critical_ok / len(CRITICAL_FIELDS), 4) if CRITICAL_FIELDS else 0.0,
        "relevant_fields_total": len(RELEVANT_FIELDS),
        "relevant_fields_ok": relevant_ok,
        "informative_fields_total": len(INFORMATIVE_FIELDS),
        "informative_fields_ok": informative_ok,
        "error_count": len(errors),
        "warning_count": len(warnings),
    }
