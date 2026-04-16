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
from src.localizacion.normalization.normalizador_subdivisiones import (
    NormalizadorSubdivisiones,
)
from src.localizacion.validacion_lote.lote_localizacion import (
    LoteLocalizacionValidator,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta IIG + NORMALIZACION + DVL + VALIDACION_LOTE para subdivisiones."
    )
    parser.add_argument("--contract", required=True)
    parser.add_argument("--csv", required=True, dest="csv_path")
    parser.add_argument("--report", required=False)
    parser.add_argument("--encoding", default="utf-8-sig")
    parser.add_argument("--delimiter", default=",")
    return parser.parse_args()


def load_csv_rows(csv_path: Path, encoding: str, delimiter: str) -> list[dict[str, Any]]:
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
    return Path("data/samples/output") / f"{csv_path.stem}__lote_subdivisiones_report.json"


def print_summary(payload: dict[str, Any]) -> None:
    iig = payload["iig_summary"]
    norm = payload["normalization_summary"]
    dvl = payload["dvl_summary"]
    lote = payload["lote_summary"]

    print(f"[INFO] Entity: {payload['entity']}")
    print(f"[INFO] CSV: {payload['csv_path']}")
    print(f"[INFO] Stage: {payload['pipeline_stage']}")
    print(f"[INFO] IIG total rows: {iig['total_rows']}")
    print(f"[INFO] IIG valid rows: {iig['valid_rows']}")
    print(f"[INFO] IIG invalid rows: {iig['invalid_rows']}")

    if not iig["is_valid_batch"]:
        print("[WARN] IIG falló. No se ejecutan capas posteriores.")
        return

    print(f"[INFO] NORMALIZATION total source rows: {norm['total_source_rows']}")
    print(f"[INFO] NORMALIZATION valid source rows: {norm['valid_source_rows']}")
    print(f"[INFO] NORMALIZATION invalid source rows: {norm['invalid_source_rows']}")
    print(f"[INFO] NORMALIZATION exploded records: {norm['exploded_records_count']}")

    if not norm["is_valid_batch"]:
        print("[WARN] NORMALIZACION falló. No se ejecutan capas posteriores.")
        return

    print(f"[INFO] DVL total rows: {dvl['total_rows']}")
    print(f"[INFO] DVL valid rows: {dvl['valid_rows']}")
    print(f"[INFO] DVL invalid rows: {dvl['invalid_rows']}")

    if not dvl["is_valid_batch"]:
        print("[WARN] DVL falló. No se ejecuta VALIDACION_LOTE.")
        return

    print(f"[INFO] LOTE total rows: {lote['total_rows']}")
    print(f"[INFO] LOTE valid rows: {lote['valid_rows']}")
    print(f"[INFO] LOTE invalid rows: {lote['invalid_rows']}")
    print(f"[INFO] LOTE duplicates_detected: {lote['duplicates_detected']}")
    print(f"[INFO] LOTE conflicts_detected: {lote['conflicts_detected']}")

    if lote["is_valid_dataset"]:
        print("[OK] VALIDACION_LOTE de subdivisiones superada: dataset globalmente válido.")
    else:
        print("[WARN] VALIDACION_LOTE de subdivisiones detectó conflictos.")
        for item in lote["invalid_rows_detail"][:10]:
            print(f"  - Row {item['row_index']}:")
            for error in item["errors"]:
                field = f" field={error['field']}" if error.get("field") else ""
                print(f"      * {error['code']}{field} -> {error['message']}")


def write_report(report_path: Path, payload: dict[str, Any]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Report written to: {report_path}")


def main() -> int:
    args = parse_args()

    contract_path = Path(args.contract)
    csv_path = Path(args.csv_path)
    report_path = Path(args.report) if args.report else default_report_path(csv_path)

    try:
        rows = load_csv_rows(csv_path, args.encoding, args.delimiter)

        iig = IIGLocalizacion(contract_path=contract_path)
        iig_result = iig.validate_rows(rows)

        valid_iig_rows = [row for rr, row in zip(iig_result.results, rows) if rr.is_valid]

        normalizer = NormalizadorSubdivisiones()
        norm_result = normalizer.normalize_rows(valid_iig_rows)

        exploded_rows = [
            asdict(record)
            for rr in norm_result.results
            if rr.is_valid
            for record in rr.normalized_records
        ]

        dvl = DVLLocalizacion()
        dvl_result = dvl.validate_rows(exploded_rows)

        dvl_valid_rows = [
            rr.validated_record
            for rr in dvl_result.results
            if rr.is_valid and rr.validated_record is not None
        ]

        lote = LoteLocalizacionValidator()
        lote_result = lote.validate_rows(dvl_valid_rows)

        payload = {
            "entity": lote_result.entity,
            "contract_path": str(contract_path),
            "csv_path": str(csv_path),
            "pipeline_stage": "IIG -> NORMALIZACION_TERRITORIAL -> DVL -> VALIDACION_LOTE",
            "iig_summary": {
                "total_rows": iig_result.total_rows,
                "valid_rows": iig_result.valid_rows,
                "invalid_rows": iig_result.invalid_rows,
                "is_valid_batch": iig_result.is_valid_batch,
                "invalid_rows_detail": [
                    {
                        "row_index": rr.row_index,
                        "errors": [to_jsonable(err) for err in rr.errors],
                    }
                    for rr in iig_result.results
                    if not rr.is_valid
                ],
            },
            "normalization_summary": {
                "total_source_rows": norm_result.total_source_rows,
                "valid_source_rows": norm_result.valid_source_rows,
                "invalid_source_rows": norm_result.invalid_source_rows,
                "exploded_records_count": norm_result.exploded_records_count,
                "is_valid_batch": norm_result.is_valid_batch,
                "invalid_rows_detail": [
                    {
                        "row_index": rr.row_index,
                        "errors": [to_jsonable(err) for err in rr.errors],
                    }
                    for rr in norm_result.results
                    if not rr.is_valid
                ],
            },
            "dvl_summary": {
                "total_rows": dvl_result.total_rows,
                "valid_rows": dvl_result.valid_rows,
                "invalid_rows": dvl_result.invalid_rows,
                "is_valid_batch": dvl_result.is_valid_batch,
                "invalid_rows_detail": [
                    {
                        "row_index": rr.row_index,
                        "errors": [to_jsonable(err) for err in rr.errors],
                        "warnings": [to_jsonable(w) for w in rr.warnings],
                    }
                    for rr in dvl_result.results
                    if not rr.is_valid
                ],
            },
            "lote_summary": {
                "total_rows": lote_result.total_rows,
                "valid_rows": lote_result.valid_rows,
                "invalid_rows": lote_result.invalid_rows,
                "is_valid_dataset": lote_result.is_valid_dataset,
                "duplicates_detected": lote_result.duplicates_detected,
                "conflicts_detected": lote_result.conflicts_detected,
                "invalid_rows_detail": [
                    {
                        "row_index": rr.row_index,
                        "errors": [to_jsonable(err) for err in rr.errors],
                        "warnings": [to_jsonable(w) for w in rr.warnings],
                    }
                    for rr in lote_result.results
                    if not rr.is_valid
                ],
            },
            "validated_records": [
                to_jsonable(rr.validated_record)
                for rr in lote_result.results
                if rr.is_valid and rr.validated_record is not None
            ],
        }

        print_summary(payload)
        write_report(report_path, payload)

        return 0 if lote_result.is_valid_dataset else 1

    except Exception as exc:
        error_payload = {
            "status": "error",
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