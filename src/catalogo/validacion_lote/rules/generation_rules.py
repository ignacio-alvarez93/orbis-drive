from __future__ import annotations

from collections import defaultdict
from typing import Any

from ..lote_result import ValidationIssue


def build_generation_key(record: dict[str, Any]) -> str:
    return "|".join(
        " ".join(str(record.get(field, "")).strip().upper().split())
        for field in ("manufacturer_name", "model_name", "generation_name")
    )


def compute_record_completeness(record: dict[str, Any]) -> float:
    ignored = {
        "_scenario",
    }
    relevant_keys = [key for key in record.keys() if key not in ignored]
    if not relevant_keys:
        return 0.0
    populated = sum(1 for key in relevant_keys if record.get(key) is not None)
    return populated / len(relevant_keys)


def validate_generations(
    records: list[dict[str, Any]],
    grouped_by_semantic: dict[str, list[tuple[int, dict[str, Any]]]],
    sparse_generation_min_versions: int = 2,
    low_completeness_threshold: float = 0.60,
) -> tuple[list[ValidationIssue], dict[str, Any], float]:
    generation_records: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    generation_unique_versions: dict[str, set[str]] = defaultdict(set)
    completeness_values: list[float] = []

    for idx, record in enumerate(records):
        generation_key = build_generation_key(record)
        generation_records[generation_key].append((idx, record))
        semantic_key = "|".join(
            " ".join(str(record.get(field, "")).strip().upper().split())
            for field in ("manufacturer_name", "model_name", "generation_name", "version_name")
        )
        generation_unique_versions[generation_key].add(semantic_key)
        completeness_values.append(compute_record_completeness(record))

    issues: list[ValidationIssue] = []
    summary: dict[str, Any] = {}

    for generation_key, members in generation_records.items():
        unique_versions = generation_unique_versions[generation_key]
        duplicate_groups = sum(
            1
            for semantic_key in unique_versions
            if len(grouped_by_semantic.get(semantic_key, [])) > 1
        )
        avg_completeness = sum(compute_record_completeness(record) for _, record in members) / len(members)
        summary[generation_key] = {
            "records": len(members),
            "unique_versions": len(unique_versions),
            "duplicate_groups": duplicate_groups,
            "avg_completeness": round(avg_completeness, 4),
        }

        if len(unique_versions) < sparse_generation_min_versions:
            issues.append(
                ValidationIssue(
                    code="generation_low_coverage",
                    severity="warning",
                    message="La generación tiene muy pocas versiones únicas en el lote.",
                    generation_key=generation_key,
                    record_indexes=[idx for idx, _ in members],
                    details={"unique_versions": len(unique_versions)},
                )
            )

        if avg_completeness < low_completeness_threshold:
            issues.append(
                ValidationIssue(
                    code="generation_low_completeness",
                    severity="warning",
                    message="La generación presenta baja completitud media.",
                    generation_key=generation_key,
                    record_indexes=[idx for idx, _ in members],
                    details={"avg_completeness": round(avg_completeness, 4)},
                )
            )

    completeness_avg = sum(completeness_values) / len(completeness_values) if completeness_values else 0.0
    return issues, summary, completeness_avg
