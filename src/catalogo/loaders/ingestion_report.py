from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RecordResult:
    row_index: int
    status: str  # inserted | skipped_duplicate | failed
    table: str
    semantic_key: str
    message: str = ""
    record_ref: dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionReport:
    ingestion_run_id: str
    dataset_path: str
    processed: int = 0
    inserted: int = 0
    skipped_duplicates: int = 0
    failed: int = 0
    affected_tables: set[str] = field(default_factory=set)
    records: list[RecordResult] = field(default_factory=list)

    def add(self, result: RecordResult) -> None:
        self.processed += 1
        self.affected_tables.add(result.table)
        self.records.append(result)

        if result.status == "inserted":
            self.inserted += 1
        elif result.status == "skipped_duplicate":
            self.skipped_duplicates += 1
        elif result.status == "failed":
            self.failed += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "ingestion_run_id": self.ingestion_run_id,
            "dataset_path": self.dataset_path,
            "processed": self.processed,
            "inserted": self.inserted,
            "skipped_duplicates": self.skipped_duplicates,
            "failed": self.failed,
            "affected_tables": sorted(self.affected_tables),
            "records": [
                {
                    "row_index": r.row_index,
                    "status": r.status,
                    "table": r.table,
                    "semantic_key": r.semantic_key,
                    "message": r.message,
                    "record_ref": r.record_ref,
                }
                for r in self.records
            ],
        }
