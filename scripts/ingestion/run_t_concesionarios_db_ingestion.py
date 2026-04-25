from __future__ import annotations

import argparse
import json

from src.catalogo.concesionarios.dvl.dvl_concesionarios import DVLConcesionarios
from src.catalogo.concesionarios.id_resolution.id_resolution_concesionarios import IDResolutionConcesionarios
from src.catalogo.concesionarios.id_resolution.orbis_location_bridge import OrbisLocationBridge
from src.catalogo.concesionarios.iig.iig_concesionarios import IIGConcesionarios
from src.catalogo.concesionarios.loaders.t_concesionarios_loader import TConcesionariosLoader
from src.catalogo.concesionarios.normalization.normalization_concesionarios import NormalizationConcesionarios
from src.catalogo.concesionarios.pipeline.consolidation import pick_best_record
from src.catalogo.concesionarios.staging.staging_loader import StagingLoader
from src.catalogo.concesionarios.validacion_lote.validacion_lote_concesionarios import ValidacionLoteConcesionarios


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--db-path", required=True)
    args = parser.parse_args()

    records = StagingLoader.load_json(args.input)

    valid, iig_rejected = IIGConcesionarios.batch_validate(records)
    normalized = NormalizationConcesionarios.batch_normalize(valid)
    validated = DVLConcesionarios.batch_validate(normalized)

    dvl_rejected = [r for r in validated if r.classification_status == "RECHAZADO"]
    dvl_pass = [r for r in validated if r.classification_status != "RECHAZADO"]

    resolver = OrbisLocationBridge(args.db_path)
    idr = IDResolutionConcesionarios(resolver)
    resolved = idr.batch_resolve(dvl_pass)

    ingestables = [
        r for r in resolved
        if r.validated.classification_status == "INGESTABLE"
        and r.localidad_id is not None
        and r.concesionario_id is not None
        and r.semantic_key_concesionario is not None
    ]

    pendientes = [
        r for r in resolved
        if r.validated.classification_status == "PENDIENTE"
    ]

    lote_result = ValidacionLoteConcesionarios.validate(ingestables)

    duplicate_groups = lote_result.duplicates
    duplicate_keys = set(duplicate_groups.keys())

    final_ingestables = [
        r for r in ingestables
        if r.semantic_key_concesionario not in duplicate_keys
    ]

    for _, group in duplicate_groups.items():
        final_ingestables.append(pick_best_record(group))

    loader = TConcesionariosLoader(args.db_path)
    insert_result = loader.batch_insert(final_ingestables)

    output = {
        "processed": len(records),
        "iig_rejected": len(iig_rejected),
        "dvl_rejected": len(dvl_rejected),
        "pending": len(pendientes),
        "ingestable_before_lote": len(ingestables),
        "duplicate_groups": len(duplicate_groups),
        "skipped_duplicates": sum(len(g) - 1 for g in duplicate_groups.values()),
        "final_ingestable": len(final_ingestables),
        "inserted": insert_result["inserted"],
        "duplicates_db": insert_result["duplicates"],
        "failed": insert_result["failed"],
        "sample_errors": insert_result["errors"],
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()