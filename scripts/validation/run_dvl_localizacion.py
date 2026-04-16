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
from src.localizacion.normalization.normalizador_paises import NormalizadorPaises


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta IIG + NORMALIZACION + DVL para T_Paises."
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

        for idx, row in enumerate(reader, start=1):
            clean_row = {k.strip(): v for k, v in row.items() if k}
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
    return Path("data/samples/output") / f"{csv_path.stem}__dvl_paises_report.json"


def main() -> int:
    args = parse_args()

    contract_path = Path(args.contract)
    csv_path = Path(args.csv_path)
    report_path = Path(args.report) if args.report else default_report_path(csv_path)

    try:
        rows = load_csv_rows(csv_path, args.encoding, args.delimiter)

        iig = IIGLocalizacion(contract_path=contract_path)
        iig_result = iig.validate_rows(rows)

        if not iig_result.is_valid_batch:
            print("[WARN] IIG falló")
            return 1

        valid_rows = [
            row for r, row in zip(iig_result.results, rows) if r.is_valid
        ]

        normalizer = NormalizadorPaises()
        norm_result = normalizer.normalize_rows(valid_rows)

        if not norm_result.is_valid_batch:
            print("[WARN] Normalización falló")
            return 1

        normalized_rows = [
            asdict(r.normalized_record)
            for r in norm_result.results
            if r.is_valid and r.normalized_record
        ]

        dvl = DVLLocalizacion()
        dvl_result = dvl.validate_rows(normalized_rows)

        print(f"[INFO] DVL valid rows: {dvl_result.valid_rows}")
        print(f"[INFO] DVL invalid rows: {dvl_result.invalid_rows}")

        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(to_jsonable(dvl_result), f, indent=2, ensure_ascii=False)

        print(f"[INFO] Report written to: {report_path}")

        return 0 if dvl_result.is_valid_batch else 1

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
