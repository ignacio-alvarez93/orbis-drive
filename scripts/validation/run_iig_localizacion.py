from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

# Ajusta este import si finalmente renombras la clase o el módulo.
from src.localizacion.iig.iig_localizacion import IIGLocalizacion


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta IIG_Localizacion sobre un CSV territorial."
    )
    parser.add_argument(
        "--contract",
        required=True,
        help="Ruta al contrato JSON. Ej: contracts/localizacion/t_paises.contract.json",
    )
    parser.add_argument(
        "--csv",
        required=True,
        dest="csv_path",
        help="Ruta al CSV de entrada. Ej: data/truth/localizacion/espana/raw/paises_es.csv",
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

                normalized_key = key.strip()
                clean_row[normalized_key] = value

            clean_row["_source_file"] = str(csv_path)
            clean_row["_row_index"] = idx
            rows.append(clean_row)

    return rows


def dataclass_to_dict(obj: Any) -> Any:
    """
    Convierte recursivamente dataclasses a dict/list para serialización JSON.
    """
    if is_dataclass(obj):
        return {k: dataclass_to_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: dataclass_to_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [dataclass_to_dict(v) for v in obj]
    return obj


def build_summary(batch_result: Any, contract_path: Path, csv_path: Path) -> dict[str, Any]:
    row_results = batch_result.results

    invalid_rows = [
        {
            "row_index": row.row_index,
            "errors": [dataclass_to_dict(err) for err in row.errors],
        }
        for row in row_results
        if not row.is_valid
    ]

    return {
        "entity": batch_result.entity,
        "contract_name": batch_result.contract_name,
        "contract_path": str(contract_path),
        "csv_path": str(csv_path),
        "total_rows": batch_result.total_rows,
        "valid_rows": batch_result.valid_rows,
        "invalid_rows": batch_result.invalid_rows,
        "is_valid_batch": batch_result.is_valid_batch,
        "invalid_rows_detail": invalid_rows,
    }


def print_console_summary(summary: dict[str, Any]) -> None:
    print(f"[INFO] Entity: {summary['entity']}")
    print(f"[INFO] Contract: {summary['contract_name']}")
    print(f"[INFO] CSV: {summary['csv_path']}")
    print(f"[INFO] Total rows: {summary['total_rows']}")
    print(f"[INFO] Valid rows: {summary['valid_rows']}")
    print(f"[INFO] Invalid rows: {summary['invalid_rows']}")

    if summary["is_valid_batch"]:
        print("[OK] IIG_Localizacion superado: lote estructuralmente válido.")
    else:
        print("[WARN] IIG_Localizacion detectó errores estructurales.")

        # Muestra hasta 10 filas inválidas para no saturar consola.
        preview = summary["invalid_rows_detail"][:10]
        for item in preview:
            print(f"  - Row {item['row_index']}:")
            for error in item["errors"]:
                field = f" field={error['field']}" if error.get("field") else ""
                print(
                    f"      * {error['code']}{field} -> {error['message']}"
                )

        remaining = len(summary["invalid_rows_detail"]) - len(preview)
        if remaining > 0:
            print(f"  ... y {remaining} filas inválidas adicionales.")


def write_report(report_path: Path, payload: dict[str, Any]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Report written to: {report_path}")


def default_report_path(csv_path: Path, contract_path: Path) -> Path:
    stem_csv = csv_path.stem
    stem_contract = contract_path.stem
    return Path("data/samples/output") / f"{stem_csv}__{stem_contract}__iig_report.json"


def main() -> int:
    args = parse_args()

    contract_path = Path(args.contract)
    csv_path = Path(args.csv_path)
    report_path = Path(args.report) if args.report else default_report_path(csv_path, contract_path)

    try:
        rows = load_csv_rows(
            csv_path=csv_path,
            encoding=args.encoding,
            delimiter=args.delimiter,
        )

        validator = IIGLocalizacion(contract_path=contract_path)
        batch_result = validator.validate_rows(rows)

        summary = build_summary(
            batch_result=batch_result,
            contract_path=contract_path,
            csv_path=csv_path,
        )

        print_console_summary(summary)
        write_report(report_path, summary)

        return 0 if summary["is_valid_batch"] else 1

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