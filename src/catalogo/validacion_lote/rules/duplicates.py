from __future__ import annotations

from collections import defaultdict
from typing import Any

from ..lote_result import ValidationIssue
from src.catalogo.validacion_lote.rules.semantic_key_v2 import (
    build_duplicate_key,
)

def group_by_duplicate_key(records: list[dict[str, Any]]) -> dict[str, list[tuple[int, dict[str, Any]]]]:
    grouped: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for idx, record in enumerate(records):
        grouped[build_duplicate_key(record)].append((idx, record))
    return dict(grouped)

def _comparable_payload(record: dict[str, Any]) -> tuple:
    ignored = {
        "_scenario",
        "scrape_date",
        "scrape_timestamp",
        "source_date_modified",
    }
    items = []
    for key in sorted(record.keys()):
        if key in ignored:
            continue
        value = record[key]
        if isinstance(value, str):
            value = " ".join(value.strip().split())
        items.append((key, value))
    return tuple(items)

def detect_duplicates(records: list[dict[str, Any]]):
    issues: list[ValidationIssue] = []
    grouped = group_by_duplicate_key(records)

    for duplicate_key, members in grouped.items():
        if len(members) <= 1:
            continue

        payloads = {_comparable_payload(record) for _, record in members}
        duplicate_kind = "exact" if len(payloads) == 1 else "semantic"

        issues.append(
            ValidationIssue(
                code=f"duplicate_{duplicate_kind}",
                severity="warning",
                message=f"Se detectaron {len(members)} registros para la misma versión semántica.",
                semantic_key=duplicate_key,
                generation_key="|".join(duplicate_key.split("|")[:3]),
                record_indexes=[idx for idx, _ in members],
                details={
                    "duplicate_kind": duplicate_kind,
                    "records_in_group": len(members),
                },
            )
        )

    return issues, grouped
