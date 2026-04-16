from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from src.catalogo.enrichment.core.enrichment_engine import EnrichmentEngine
from src.catalogo.loaders.ingestion_report import IngestionReport, RecordResult
from src.catalogo.loaders.reference_resolver import ReferenceResolver
from src.catalogo.loaders.t_versiones_loader import TVersionesLoader


class IngestionError(Exception):
    pass


class TVersionesIngestionPipeline:
    """
    Pipeline REAL (sin modo piloto)

    - Sin límite de tamaño de lote
    - Compatible con reingestión
    - Compatible con pipeline completo
    - Seguro frente a transacciones anidadas
    """

    def __init__(self, conn, strict_batch: bool = True):
        self.conn = conn
        self.strict_batch = strict_batch
        self.resolver = ReferenceResolver(conn)
        self.loader = TVersionesLoader(conn)
        self.enrichment_engine = EnrichmentEngine()

    def _prevalidate_row(self, row: dict[str, Any], row_index: int) -> None:
        required_pipeline_flags = {
            "iig_status": "passed",
            "dvl_status": "passed",
        }

        if "batch_status" in row:
            required_pipeline_flags["batch_status"] = "passed"

        for field, expected in required_pipeline_flags.items():
            if row.get(field) != expected:
                raise IngestionError(
                    f"Fila {row_index}: {field}={row.get(field)!r} no válido; esperado {expected!r}"
                )

        required_business_fields = [
            "manufacturer_name",
            "model_name",
            "version_name",
        ]
        for field in required_business_fields:
            if not row.get(field):
                raise IngestionError(
                    f"Fila {row_index}: falta campo obligatorio {field}"
                )

    def _load_rows(self, dataset_path: str) -> list[dict[str, Any]]:
        dataset_file = Path(dataset_path)
        rows = json.loads(dataset_file.read_text(encoding="utf-8"))

        if not isinstance(rows, list):
            raise IngestionError("El dataset debe ser una lista JSON.")

        if len(rows) == 0:
            raise IngestionError("El dataset no puede estar vacío.")

        for row in rows:
            row["_source_dataset"] = str(dataset_file)

        return rows

    def _build_row_for_resolution(self, row: dict[str, Any]):
        enrichment_result = self.enrichment_engine.run(row)

        row_for_resolution = {
            **row,
            **enrichment_result.enriched_fields,
            "_enrichment": enrichment_result.to_dict(),
        }

        return row_for_resolution, enrichment_result.to_dict()

    def run(self, dataset_path: str) -> IngestionReport:
        rows = self._load_rows(dataset_path)
        ingestion_run_id = str(uuid.uuid4())

        report = IngestionReport(
            ingestion_run_id=ingestion_run_id,
            dataset_path=dataset_path,
        )

        # Si ya hay una transacción abierta (por ejemplo, desde reingestión),
        # no abrimos ni cerramos otra aquí.
        owns_transaction = not self.conn.in_transaction

        try:
            if owns_transaction:
                self.conn.execute("BEGIN")

            for idx, row in enumerate(rows, start=1):
                try:
                    self._prevalidate_row(row, idx)

                    row_for_resolution, enrichment_payload = self._build_row_for_resolution(row)

                    refs = self.resolver.resolve_all(row_for_resolution)

                    result = self.loader.insert_one(
                        row_index=idx,
                        row=row_for_resolution,
                        refs=refs,
                        ingestion_run_id=ingestion_run_id,
                    )

                    if isinstance(result.record_ref, dict):
                        result.record_ref["enrichment"] = enrichment_payload

                    report.add(result)

                except Exception as exc:
                    report.add(RecordResult(
                        row_index=idx,
                        status="failed",
                        table="T_Versiones",
                        semantic_key="UNAVAILABLE",
                        message=str(exc),
                        record_ref=row,
                    ))
                    if self.strict_batch:
                        raise

            if owns_transaction:
                self.conn.commit()
            return report

        except Exception:
            if owns_transaction:
                self.conn.rollback()
            if self.strict_batch:
                raise
            return report
