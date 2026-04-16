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
from src.localizacion.normalization.normalizador_localidades import (
    NormalizadorLocalidades,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta IIG + NORMALIZACION + DVL para T_Localidades."
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
    return Path("data/samples/output") / f"{csv_path.stem}__dvl_localidades_report.json"


def print_summary(payload: dict[str, Any]) -> None:
    iig = payload["iig_summary"]
    norm = payload["normalization_summary"]
    dvl = payload["dvl_summary"]

    print(f"[INFO] Entity: {payload['entity']}")
    print(f"[INFO] CSV: {payload['csv_path']}")
    print(f"[INFO] Stage: {payload['pipeline_stage']}")
    print(f"[INFO] IIG total rows: {iig['total_rows']}")
    print(f"[INFO] IIG valid rows: {iig['valid_rows']}")
    print(f"[INFO] IIG invalid rows: {iig['invalid_rows']}")

    if not iig["is_valid_batch"]:
        print("[WARN] IIG falló. No se ejecutan capas posteriores.")
        return

    print(f"[INFO] NORMALIZATION total rows: {norm['total_rows']}")
    print(f"[INFO] NORMALIZATION valid rows: {norm['valid_rows']}")
    print(f"[INFO] NORMALIZATION invalid rows: {norm['invalid_rows']}")

    if not norm["is_valid_batch"]:
        print("[WARN] NORMALIZACION falló. No se ejecuta DVL.")
        return

    print(f"[INFO] DVL total rows: {dvl['total_rows']}")
    print(f"[INFO] DVL valid rows: {dvl['valid_rows']}")
    print(f"[INFO] DVL invalid rows: {dvl['invalid_rows']}")

    if dvl["is_valid_batch"]:
        print("[OK] DVL de localidades superado: lote semánticamente válido.")
    else:
        print("[WARN] DVL de localidades detectó incidencias.")
        for item in dvl["invalid_rows_detail"][:10]:
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

        normalizer = NormalizadorLocalidades()
        norm_result = normalizer.normalize_rows(valid_iig_rows)

        normalized_rows = [
            asdict(rr.normalized_record)
            for rr in norm_result.results
            if rr.is_valid and rr.normalized_record is not None
        ]

        dvl = DVLLocalizacion()
        dvl_result = dvl.validate_rows(normalized_rows)

        payload = {
            "entity": dvl_result.entity,
            "contract_path": str(contract_path),
            "csv_path": str(csv_path),
            "pipeline_stage": "IIG -> NORMALIZACION_TERRITORIAL -> DVL",
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
                "total_rows": norm_result.total_rows,
                "valid_rows": norm_result.valid_rows,
                "invalid_rows": norm_result.invalid_rows,
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
            "validated_records": [
                to_jsonable(rr.validated_record)
                for rr in dvl_result.results
                if rr.is_valid and rr.validated_record is not None
            ],
        }

        print_summary(payload)
        write_report(report_path, payload)

        return 0 if dvl_result.is_valid_batch else 1

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