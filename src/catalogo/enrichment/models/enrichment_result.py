from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class FieldTrace:
    field: str
    source: str
    rule: str
    confidence: str = "deterministic"


@dataclass
class EnrichmentResult:
    original_data: Dict[str, Any]
    enriched_fields: Dict[str, Any] = field(default_factory=dict)
    trace: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    applied_rules: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def add_field(
        self,
        *,
        field_name: str,
        value: Any,
        source: str,
        rule: str,
        confidence: str = "deterministic",
    ) -> None:
        """
        Añade un campo enriquecido sin sobrescribir verdad base válida.
        Permite rellenar campos existentes si están a NULL.
        """

        # SOLO bloquear si el campo existe Y tiene valor real
        if field_name in self.original_data and self.original_data[field_name] is not None:
            return

        if field_name in self.enriched_fields:
            return

        self.enriched_fields[field_name] = value
        self.trace[field_name] = {
            "field": field_name,
            "source": source,
            "rule": rule,
            "confidence": confidence,
        }

    def finalize(self) -> "EnrichmentResult":
        original_len = len(self.original_data) if self.original_data else 0
        enriched_len = len(self.enriched_fields)
        self.metrics = {
            "enriched_fields_count": enriched_len,
            "enrichment_ratio": (enriched_len / original_len) if original_len else 0.0,
        }
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_data": self.original_data,
            "enriched_fields": self.enriched_fields,
            "trace": self.trace,
            "applied_rules": self.applied_rules,
            "metrics": self.metrics,
        }
