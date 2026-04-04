from __future__ import annotations

import hashlib
from typing import Any

from src.catalogo.loaders.ingestion_report import RecordResult
from src.catalogo.loaders.reference_resolver import ResolvedReferences


UNIQUE_FIELDS = [
    "version_name",
    "body_type",
    "fuel_type",
    "power_cv",
    "gearbox",
    "traction",
]


def build_semantic_key(refs: ResolvedReferences, row: dict[str, Any]) -> str:
    raw = "|".join([
        str(refs.manufacturer_id),
        str(refs.model_id),
        str(refs.generation_id) if refs.generation_id is not None else "NULL",
        *[str(row.get(field, "")) for field in UNIQUE_FIELDS],
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class TVersionesLoader:
    def __init__(self, conn):
        self.conn = conn

    def exists(self, semantic_key: str) -> bool:
        cur = self.conn.execute(
            "SELECT 1 FROM T_Versiones WHERE semantic_key = ? LIMIT 1",
            (semantic_key,),
        )
        return cur.fetchone() is not None

    def insert_one(
        self,
        row_index: int,
        row: dict[str, Any],
        refs: ResolvedReferences,
        ingestion_run_id: str,
    ) -> RecordResult:
        semantic_key = build_semantic_key(refs, row)

        if self.exists(semantic_key):
            return RecordResult(
                row_index=row_index,
                status="skipped_duplicate",
                table="T_Versiones",
                semantic_key=semantic_key,
                message="Registro omitido por duplicado semántico.",
                record_ref={
                    "manufacturer_id": refs.manufacturer_id,
                    "model_id": refs.model_id,
                    "generation_id": refs.generation_id,
                    "version_name": row.get("version_name"),
                },
            )

        self.conn.execute(
            """
            INSERT INTO T_Versiones (
                manufacturer_id,
                model_id,
                generation_id,
                version_name,
                body_type,
                fuel_type,
                power_cv,
                gearbox,
                traction,
                source_dataset,
                ingestion_run_id,
                semantic_key
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                refs.manufacturer_id,
                refs.model_id,
                refs.generation_id,
                row.get("version_name"),
                row.get("body_type"),
                row.get("fuel_type"),
                row.get("power_cv"),
                row.get("gearbox"),
                row.get("traction"),
                row.get("_source_dataset"),
                ingestion_run_id,
                semantic_key,
            ),
        )

        return RecordResult(
            row_index=row_index,
            status="inserted",
            table="T_Versiones",
            semantic_key=semantic_key,
            message="Registro insertado correctamente.",
            record_ref={
                "manufacturer_id": refs.manufacturer_id,
                "model_id": refs.model_id,
                "generation_id": refs.generation_id,
                "version_name": row.get("version_name"),
            },
        )
