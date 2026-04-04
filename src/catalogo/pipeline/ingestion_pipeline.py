from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from src.catalogo.loaders.ingestion_report import IngestionReport, RecordResult
from src.catalogo.loaders.reference_resolver import ReferenceResolver
from src.catalogo.loaders.t_versiones_loader import TVersionesLoader


class PilotIngestionError(Exception):
    """Error controlado de ingestión piloto."""


class TVersionesPilotIngestionPipeline:
    def __init__(self, conn, strict_batch: bool = True):
        self.conn = conn
        self.strict_batch = strict_batch
        self.resolver = ReferenceResolver(conn)
        self.loader = TVersionesLoader(conn)

    def _prevalidate_row(self, row: dict[str, Any], row_index: int) -> None:
        required_pipeline_flags = {
            "iig_status": "passed",
            "dvl_status": "passed",
            "batch_status": "passed",
        }
        for field, expected in required_pipeline_flags.items():
            if row.get(field) != expected:
                raise PilotIngestionError(
                    f"Fila {row_index}: {field}={row.get(field)!r} no válido; esperado {expected!r}"
                )

        required_business_fields = [
            "manufacturer_name",
            "model_name",
            "version_name",
        ]
        for field in required_business_fields:
            value = row.get(field)
            if value in (None, ""):
                raise PilotIngestionError(
                    f"Fila {row_index}: falta campo obligatorio de ingestión {field!r}"
                )

    def _load_rows(self, dataset_path: str) -> list[dict[str, Any]]:
        dataset_file = Path(dataset_path)
        rows = json.loads(dataset_file.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise PilotIngestionError("El dataset de ingestión debe ser una lista JSON.")
        if not (3 <= len(rows) <= 5):
            raise PilotIngestionError(
                f"Lote piloto inválido: se esperaban entre 3 y 5 registros y llegaron {len(rows)}"
            )
        for row in rows:
            row["_source_dataset"] = str(dataset_file)
        return rows

    def run(self, dataset_path: str) -> IngestionReport:
        rows = self._load_rows(dataset_path)
        ingestion_run_id = str(uuid.uuid4())
        report = IngestionReport(
            ingestion_run_id=ingestion_run_id,
            dataset_path=dataset_path,
        )

        try:
            self.conn.execute("BEGIN")

            for idx, row in enumerate(rows, start=1):
                try:
                    self._prevalidate_row(row, idx)
                    refs = self.resolver.resolve_all(row)
                    result = self.loader.insert_one(
                        row_index=idx,
                        row=row,
                        refs=refs,
                        ingestion_run_id=ingestion_run_id,
                    )
                    report.add(result)
                except Exception as exc:
                    result = RecordResult(
                        row_index=idx,
                        status="failed",
                        table="T_Versiones",
                        semantic_key="UNAVAILABLE",
                        message=str(exc),
                        record_ref={
                            "manufacturer_name": row.get("manufacturer_name"),
                            "model_name": row.get("model_name"),
                            "version_name": row.get("version_name"),
                        },
                    )
                    report.add(result)
                    if self.strict_batch:
                        raise

            self.conn.commit()
            return report

        except Exception:
            self.conn.rollback()
            if self.strict_batch:
                raise
            return report
