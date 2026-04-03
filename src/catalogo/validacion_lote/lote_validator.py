from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .lote_result import DatasetMetrics, LoteValidationResult, ValidationIssue
from .rules.conflicts import detect_group_conflicts, detect_internal_record_conflicts
from .rules.duplicates import build_semantic_key, detect_duplicates
from .rules.generation_rules import validate_generations
from .rules.outliers import detect_outliers


@dataclass(slots=True)
class LoteValidatorConfig:
    sparse_generation_min_versions: int = 2
    low_completeness_threshold: float = 0.60


class LoteValidator:
    def __init__(self, config: LoteValidatorConfig | None = None) -> None:
        self.config = config or LoteValidatorConfig()

    def validate(self, records: list[dict[str, Any]]) -> LoteValidationResult:
        if not isinstance(records, list):
            raise TypeError("records must be a list of dictionaries")
        if not all(isinstance(record, dict) for record in records):
            raise TypeError("every record must be a dictionary")

        duplicate_issues, grouped_by_semantic = detect_duplicates(records)
        conflict_issues = detect_group_conflicts(grouped_by_semantic)
        conflict_issues.extend(detect_internal_record_conflicts(records))
        outlier_issues = detect_outliers(records)
        generation_warnings, generation_summary, completeness_avg = validate_generations(
            records,
            grouped_by_semantic,
            sparse_generation_min_versions=self.config.sparse_generation_min_versions,
            low_completeness_threshold=self.config.low_completeness_threshold,
        )

        warnings = duplicate_issues + outlier_issues + generation_warnings
        errors = conflict_issues

        metrics = DatasetMetrics(
            total_records=len(records),
            unique_versions=len({build_semantic_key(record) for record in records}),
            duplicates=len(duplicate_issues),
            conflicts=len(errors),
            warnings=len(warnings),
            completeness_avg=completeness_avg,
            generations=len(generation_summary),
        )

        return LoteValidationResult(
            is_valid_dataset=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics=metrics,
            generation_summary=generation_summary,
        )
