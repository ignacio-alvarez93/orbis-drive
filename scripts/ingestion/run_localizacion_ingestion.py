from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from src.localizacion.dvl.dvl_localizacion import DVLLocalizacion
from src.localizacion.iig.iig_localizacion import IIGLocalizacion
from src.localizacion.id_resolution.id_resolution_localizacion import (
    IDResolutionLocalizacion,
)
from src.localizacion.loaders.localizacion_loader import LocalizacionLoader
from src.localizacion.normalization.normalizador_paises import NormalizadorPaises
from src.localizacion.validacion_lote.lote_localizacion import (
    LoteLocalizacionValidator,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta el pipeline completo e ingesta T_Paises en SQLite."
    )
    parser.add_argument("--db-path", required=True, help="Ruta a la base SQLite.")
    parser.add_argument("--contract", required=True, help="Ruta al contrato JSON.")
    parser.add_argument("--csv", required=True, dest="csv_path", help="Ruta al CSV de entrada.")
    parser.add_argument("--report", required=False, help="Ruta opcional del reporte JSON.")
    parser.add_argument("--encoding", default="utf-8-sig")
    parser.add_argument("--delimiter", default=",")
    parser.add_argument("--dry-run", action="store_true", help="No escribe en DB.")
    return parser.parse_args()


def load_csv_rows(csv_path: Path, encoding: str, delimiter: str) -> list[dict[str, Any]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"No existe el CSV: {csv_path}")

    rows: list[dict[str, Any]] = []
    with csv_path.open("r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError(f"El CSV no contiene cabecera: {csv_path}")

        for idx, row in enumerate(reader, start=1):
            clean_row = {k.strip(): v for k, v in row.items() if k is not None}
            clean_row["_source_file"] = str(csv_path)
            clean_row["_row_index"] = idx
            rows.append(clean_row)

    return rows


def to_jsonable(obj: Any) -> Any:
    if is_dataclass(obj):
        return {k: to_jsonable(v) for k, v in asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_jsonable(v) for v in obj]
    return obj


def default_report_path(csv_path: Path) -> Path:
    return Path("data/samples/output") / f"{csv_path.stem}__ingestion_paises_report.json"


def write_report(report_path: Path, payload: dict[str, Any]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Report written to: {report_path}")


def main() -> int:
    args = parse_args()

    db_path = Path(args.db_path)
    contract_path = Path(args.contract)
    csv_path = Path(args.csv_path)
    report_path = Path(args.report) if args.report else default_report_path(csv_path)

    try:
        rows = load_csv_rows(csv_path, args.encoding, args.delimiter)

        iig = IIGLocalizacion(contract_path=contract_path)
        iig_result = iig.validate_rows(rows)
        if not iig_result.is_valid_batch:
            raise ValueError("IIG falló. La ingestión no puede continuar.")

        valid_iig_rows = [row for rr, row in zip(iig_result.results, rows) if rr.is_valid]

        normalizer = NormalizadorPaises()
        norm_result = normalizer.normalize_rows(valid_iig_rows)
        if not norm_result.is_valid_batch:
            raise ValueError("NORMALIZACION falló. La ingestión no puede continuar.")

        normalized_rows = [
            asdict(rr.normalized_record)
            for rr in norm_result.results
            if rr.is_valid and rr.normalized_record is not None
        ]

        dvl = DVLLocalizacion()
        dvl_result = dvl.validate_rows(normalized_rows)
        if not dvl_result.is_valid_batch:
            raise ValueError("DVL falló. La ingestión no puede continuar.")

        dvl_valid_rows = [
            rr.validated_record
            for rr in dvl_result.results
            if rr.is_valid and rr.validated_record is not None
        ]

        lote = LoteLocalizacionValidator()
        lote_result = lote.validate_rows(dvl_valid_rows)
        if not lote_result.is_valid_dataset:
            raise ValueError("VALIDACION_LOTE falló. La ingestión no puede continuar.")

        lote_valid_rows = [
            rr.validated_record
            for rr in lote_result.results
            if rr.is_valid and rr.validated_record is not None
        ]

        idr = IDResolutionLocalizacion()
        idr_result = idr.resolve_rows(lote_valid_rows)
        if not idr_result.is_valid_batch:
            raise ValueError("ID_RESOLUTION falló. La ingestión no puede continuar.")

        resolved_rows = [
            rr.resolved_record
            for rr in idr_result.results
            if rr.is_valid and rr.resolved_record is not None
        ]

        loader = LocalizacionLoader(db_path=db_path)
        ingestion_result = loader.ingest_paises(
            rows=resolved_rows,
            dry_run=args.dry_run,
        )

        payload = {
            "entity": ingestion_result.entity,
            "db_path": str(db_path),
            "contract_path": str(contract_path),
            "csv_path": str(csv_path),
            "dry_run": args.dry_run,
            "pipeline_stage": (
                "IIG -> NORMALIZACION_TERRITORIAL -> DVL -> "
                "VALIDACION_LOTE -> ID_RESOLUTION -> INGESTION"
            ),
            "ingestion_summary": {
                "processed": ingestion_result.processed,
                "inserted": ingestion_result.inserted,
                "skipped_existing": ingestion_result.skipped_existing,
                "failed": ingestion_result.failed,
                "is_successful": ingestion_result.is_successful,
            },
            "row_results": [to_jsonable(r) for r in ingestion_result.results],
        }

        print(f"[INFO] Processed: {ingestion_result.processed}")
        print(f"[INFO] Inserted: {ingestion_result.inserted}")
        print(f"[INFO] Skipped existing: {ingestion_result.skipped_existing}")
        print(f"[INFO] Failed: {ingestion_result.failed}")
        if args.dry_run:
            print("[WARN] Dry run activo: no se han escrito cambios en DB.")

        write_report(report_path, payload)

        return 0 if ingestion_result.is_successful else 1

    except Exception as exc:
        error_payload = {
            "status": "error",
            "db_path": str(db_path),
            "contract_path": str(contract_path),
            "csv_path": str(csv_path),
            "message": str(exc),
        }
        print(f"[ERROR] {exc}", file=sys.stderr)
        try:
            write_report(report_path, error_payload)
        except Exception:
            pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main())