from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from src.localizacion.iig.iig_localizacion import IIGLocalizacion
from src.localizacion.normalization.normalizador_subdivisiones import (
    NormalizadorSubdivisiones,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta IIG + NORMALIZACION_TERRITORIAL para T_Subdivisiones_Administrativas."
    )
    parser.add_argument(
        "--contract",
        required=True,
        help="Ruta al contrato JSON de subdivisiones.",
    )
    parser.add_argument(
        "--csv",
        required=True,
        dest="csv_path",
        help="Ruta al CSV fuente de subdivisiones.",
    )
    parser.add_argument(
        "--report",
        required=False,
        help="Ruta opcional del reporte JSON de salida.",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="Encoding del CSV. Por defecto: utf-8-sig",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        help="Delimitador del CSV. Por defecto: ','",
    )
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
            clean_row: dict[str, Any] = {}

            for key, value in row.items():
                if key is None:
                    continue
                clean_row[key.strip()] = value

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
    return Path("data/samples/output") / f"{csv_path.stem}__normalizacion_subdivisiones_report.json"


def build_payload(
    contract_path: Path,
    csv_path: Path,
    iig_batch_result: Any,
    normalization_batch_result: Any,
) -> dict[str, Any]:
    iig_invalid_rows = [
        {
            "row_index": row.row_index,
            "errors": [to_jsonable(err) for err in row.errors],
        }
        for row in iig_batch_result.results
        if not row.is_valid
    ]

    normalization_invalid_rows = [
        {
            "row_index": row.row_index,
            "errors": [to_jsonable(err) for err in row.errors],
        }
        for row in normalization_batch_result.results
        if not row.is_valid
    ]

    exploded_records = []
    for row_result in normalization_batch_result.results:
        if row_result.is_valid:
            exploded_records.extend(
                [to_jsonable(record) for record in row_result.normalized_records]
            )

    return {
        "entity": normalization_batch_result.entity,
        "contract_path": str(contract_path),
        "csv_path": str(csv_path),
        "pipeline_stage": "IIG -> NORMALIZACION_TERRITORIAL",
        "iig_summary": {
            "total_rows": iig_batch_result.total_rows,
            "valid_rows": iig_batch_result.valid_rows,
            "invalid_rows": iig_batch_result.invalid_rows,
            "is_valid_batch": iig_batch_result.is_valid_batch,
            "invalid_rows_detail": iig_invalid_rows,
        },
        "normalization_summary": {
            "total_source_rows": normalization_batch_result.total_source_rows,
            "valid_source_rows": normalization_batch_result.valid_source_rows,
            "invalid_source_rows": normalization_batch_result.invalid_source_rows,
            "exploded_records_count": normalization_batch_result.exploded_records_count,
            "is_valid_batch": normalization_batch_result.is_valid_batch,
            "invalid_rows_detail": normalization_invalid_rows,
        },
        "exploded_records": exploded_records,
    }


def print_summary(payload: dict[str, Any]) -> None:
    iig = payload["iig_summary"]
    norm = payload["normalization_summary"]

    print(f"[INFO] Entity: {payload['entity']}")
    print(f"[INFO] CSV: {payload['csv_path']}")
    print(f"[INFO] Stage: {payload['pipeline_stage']}")
    print(f"[INFO] IIG total rows: {iig['total_rows']}")
    print(f"[INFO] IIG valid rows: {iig['valid_rows']}")
    print(f"[INFO] IIG invalid rows: {iig['invalid_rows']}")

    if not iig["is_valid_batch"]:
        print("[WARN] IIG falló. No se ejecuta normalización.")
        return

    print(f"[INFO] NORMALIZATION total source rows: {norm['total_source_rows']}")
    print(f"[INFO] NORMALIZATION valid source rows: {norm['valid_source_rows']}")
    print(f"[INFO] NORMALIZATION invalid source rows: {norm['invalid_source_rows']}")
    print(f"[INFO] NORMALIZATION exploded records: {norm['exploded_records_count']}")

    if norm["is_valid_batch"]:
        print("[OK] Normalización de subdivisiones completada correctamente.")
    else:
        print("[WARN] La normalización de subdivisiones detectó incidencias.")
        for item in norm["invalid_rows_detail"][:10]:
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
        rows = load_csv_rows(
            csv_path=csv_path,
            encoding=args.encoding,
            delimiter=args.delimiter,
        )

        iig = IIGLocalizacion(contract_path=contract_path)
        iig_batch_result = iig.validate_rows(rows)

        if not iig_batch_result.is_valid_batch:
            payload = {
                "entity": iig_batch_result.entity,
                "contract_path": str(contract_path),
                "csv_path": str(csv_path),
                "pipeline_stage": "IIG -> NORMALIZACION_TERRITORIAL",
                "iig_summary": {
                    "total_rows": iig_batch_result.total_rows,
                    "valid_rows": iig_batch_result.valid_rows,
                    "invalid_rows": iig_batch_result.invalid_rows,
                    "is_valid_batch": iig_batch_result.is_valid_batch,
                    "invalid_rows_detail": [
                        {
                            "row_index": row.row_index,
                            "errors": [to_jsonable(err) for err in row.errors],
                        }
                        for row in iig_batch_result.results
                        if not row.is_valid
                    ],
                },
                "normalization_summary": None,
                "exploded_records": [],
            }
            print_summary(payload)
            write_report(report_path, payload)
            return 1

        valid_iig_rows = [
            row
            for row_result, row in zip(iig_batch_result.results, rows)
            if row_result.is_valid
        ]

        normalizer = NormalizadorSubdivisiones()
        normalization_batch_result = normalizer.normalize_rows(valid_iig_rows)

        payload = build_payload(
            contract_path=contract_path,
            csv_path=csv_path,
            iig_batch_result=iig_batch_result,
            normalization_batch_result=normalization_batch_result,
        )

        print_summary(payload)
        write_report(report_path, payload)

        return 0 if normalization_batch_result.is_valid_batch else 1

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