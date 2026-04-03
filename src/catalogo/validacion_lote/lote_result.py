from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ValidationIssue:
    code: str
    severity: str
    message: str
    semantic_key: str | None = None
    generation_key: str | None = None
    record_indexes: list[int] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DatasetMetrics:
    total_records: int
    unique_versions: int
    duplicates: int
    conflicts: int
    warnings: int
    completeness_avg: float
    generations: int

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["completeness_avg"] = round(self.completeness_avg, 4)
        return payload


@dataclass(slots=True)
class LoteValidationResult:
    is_valid_dataset: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    metrics: DatasetMetrics | None = None
    generation_summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid_dataset": self.is_valid_dataset,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "generation_summary": self.generation_summary,
        }
