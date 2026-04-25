from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ..dvl.dvl_concesionarios import DVLConcesionarios
from ..enrichment.enrichment_engine import EnrichmentConcesionariosEngine
from ..id_resolution.id_resolution_concesionarios import IDResolutionConcesionarios
from ..iig.iig_concesionarios import IIGConcesionarios
from ..models.pipeline_result import PipelineResult
from ..normalization.normalization_concesionarios import NormalizationConcesionarios
from ..staging.staging_loader import StagingLoader
from ..validacion_lote.validacion_lote_concesionarios import (
    ValidacionLoteConcesionarios,
)
from .consolidation import pick_best_record


class ConcesionariosIngestionPipeline:
    def __init__(self, resolver: Any) -> None:
        self.idr = IDResolutionConcesionarios(resolver)

    def run(
        self,
        input_path: str,
        report_path: str | None = None,
    ) -> dict[str, Any]:
        result = PipelineResult()

        records = StagingLoader.load_json(input_path)
        result.processed = len(records)

        # 1) IIG
        iig_valid, iig_rejected = IIGConcesionarios.batch_validate(records)
        if iig_rejected:
            result.rejected_technical += len(iig_rejected)
            result.causes["iig_rejected"] = len(iig_rejected)

        # 2) NORMALIZATION
        normalized = NormalizationConcesionarios.batch_normalize(iig_valid)

        # 3) DVL
        validated = DVLConcesionarios.batch_validate(normalized)

        dvl_rejected = [r for r in validated if r.classification_status == "RECHAZADO"]
        if dvl_rejected:
            result.rejected_technical += len(dvl_rejected)
            result.causes["dvl_rejected"] = len(dvl_rejected)

        dvl_pass = [r for r in validated if r.classification_status != "RECHAZADO"]

        # 4) ID_RESOLUTION
        resolved = self.idr.batch_resolve(dvl_pass)

        ingestables = [
            r for r in resolved
            if r.validated.classification_status == "INGESTABLE"
        ]
        pendientes = [
            r for r in resolved
            if r.validated.classification_status == "PENDIENTE"
        ]

        result.pending_recoverable = len(pendientes)
        if pendientes:
            result.causes["pending_id_resolution"] = len(pendientes)

        # 5) VALIDACION_LOTE
        lote_result = ValidacionLoteConcesionarios.validate(ingestables)

        result.skipped_duplicates = sum(
            len(group) - 1 for group in lote_result.duplicates.values()
        )
        if result.skipped_duplicates:
            result.causes["duplicate_semantic_key"] = result.skipped_duplicates

        # Consolidación robusta:
        # - registros únicos pasan directos
        # - grupos duplicados conservan el mejor registro
        duplicate_groups = lote_result.duplicates
        duplicate_keys = set(duplicate_groups.keys())

        final_ingestables = [
            r
            for r in ingestables
            if r.semantic_key_concesionario not in duplicate_keys
        ]

        consolidated_duplicates = []
        for _, group in duplicate_groups.items():
            best = pick_best_record(group)
            consolidated_duplicates.append(best)

        final_ingestables.extend(consolidated_duplicates)

        # 6) ENRICHMENT
        enriched = EnrichmentConcesionariosEngine.batch_enrich(final_ingestables)
        result.inserted = len(enriched)

        payload = {
            "summary": asdict(result),
            "iig_rejected_count": len(iig_rejected),
            "dvl_rejected_count": len(dvl_rejected),
            "pending_count": len(pendientes),
            "ingestable_count_before_lote": len(ingestables),
            "final_ingestable_count": len(final_ingestables),
            "duplicate_groups_count": len(duplicate_groups),
            "duplicate_warnings": lote_result.duplicate_warnings,
            "conflicts": lote_result.conflicts,
            "dataset_valid": lote_result.is_valid_dataset,
            "enriched_records": [
                {
                    "concesionario_id": item.resolved.concesionario_id,
                    "semantic_key_concesionario": item.resolved.semantic_key_concesionario,
                    "source_name": item.resolved.validated.normalized.raw.source_name,
                    "source_row_url": item.resolved.validated.normalized.raw.source_row_url,
                    "record_external_id": item.resolved.validated.normalized.raw.record_external_id,
                    "dealer_name_raw": item.resolved.validated.normalized.raw.dealer_name_raw,
                    "nombre_canonical": item.resolved.validated.normalized.nombre_canonical,
                    "tipo_concesionario_normalizado": item.resolved.validated.normalized.tipo_concesionario_normalizado,
                    "classification_status": item.resolved.validated.classification_status,
                    "pais_id": item.resolved.pais_id,
                    "subdivision_id": item.resolved.subdivision_id,
                    "localidad_id": item.resolved.localidad_id,
                    "website_domain": item.website_domain,
                    "flags": item.flags,
                    "derived": item.derived,
                }
                for item in enriched
            ],
            "pending_records": [
                {
                    "source_name": r.validated.normalized.raw.source_name,
                    "source_row_url": r.validated.normalized.raw.source_row_url,
                    "record_external_id": r.validated.normalized.raw.record_external_id,
                    "dealer_name_raw": r.validated.normalized.raw.dealer_name_raw,
                    "location_raw": r.validated.normalized.raw.location_raw,
                    "postal_code_raw": r.validated.normalized.raw.postal_code_raw,
                    "warnings": r.validated.validation_warnings,
                }
                for r in pendientes
            ],
            "rejected_records": [
                {
                    "source_name": r.normalized.raw.source_name,
                    "source_row_url": r.normalized.raw.source_row_url,
                    "record_external_id": r.normalized.raw.record_external_id,
                    "dealer_name_raw": r.normalized.raw.dealer_name_raw,
                    "errors": r.validation_errors,
                    "warnings": r.validation_warnings,
                }
                for r in dvl_rejected
            ],
            "iig_rejected_records": [
                {
                    "source_name": rec.source_name,
                    "source_row_url": rec.source_row_url,
                    "record_external_id": rec.record_external_id,
                    "dealer_name_raw": rec.dealer_name_raw,
                    "errors": errors,
                }
                for rec, errors in iig_rejected
            ],
        }

        if report_path:
            p = Path(report_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        return payload