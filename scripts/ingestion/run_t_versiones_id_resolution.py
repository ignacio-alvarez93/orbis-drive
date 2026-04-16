from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.catalogo.pipeline.id_resolution.id_resolver import (
    IDResolutionError,
    resolve_dataset_file,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resuelve IDs de catálogo para un lote de T_Versiones antes de ingestión"
    )
    parser.add_argument("--db-path", required=True, help="Ruta a la SQLite operativa")
    parser.add_argument("--input", required=True, help="Dataset validado sin IDs")
    parser.add_argument("--output", required=True, help="Dataset resuelto con IDs")
    parser.add_argument(
        "--quiet-json",
        action="store_true",
        help="No imprime el resumen JSON final por stdout; solo logs operativos.",
    )
    return parser.parse_args()


def safe_print(message: str, *, file=None) -> None:
    target = file if file is not None else sys.stdout
    try:
        print(message, file=target)
    except UnicodeEncodeError:
        sanitized = message.encode("ascii", "replace").decode("ascii")
        print(sanitized, file=target)


def build_summary(output_path: str) -> dict:
    output_file = Path(output_path)
    rows = json.loads(output_file.read_text(encoding="utf-8"))

    if not isinstance(rows, list):
        raise ValueError("El fichero de salida no contiene una lista JSON.")

    total_records = len(rows)
    resolved_manufacturer = sum(1 for row in rows if row.get("manufacturer_id"))
    resolved_model = sum(1 for row in rows if row.get("model_id"))
    resolved_generation = sum(1 for row in rows if row.get("generation_id"))
    resolved_version = sum(1 for row in rows if row.get("version_id"))

    return {
        "status": "ok",
        "input_records": total_records,
        "resolved_manufacturer_id": resolved_manufacturer,
        "resolved_model_id": resolved_model,
        "resolved_generation_id": resolved_generation,
        "resolved_version_id": resolved_version,
        "output_path": str(output_file),
    }


def main() -> int:
    args = parse_args()
    try:
        resolve_dataset_file(
            db_path=args.db_path,
            input_path=args.input,
            output_path=args.output,
        )

        summary = build_summary(args.output)

        safe_print("[INFO] ID resolution completed.")
        safe_print(f"[INFO] Input records: {summary['input_records']}")
        safe_print(
            f"[INFO] Resolved manufacturer_id: {summary['resolved_manufacturer_id']}/{summary['input_records']}"
        )
        safe_print(
            f"[INFO] Resolved model_id: {summary['resolved_model_id']}/{summary['input_records']}"
        )
        safe_print(
            f"[INFO] Resolved generation_id: {summary['resolved_generation_id']}/{summary['input_records']}"
        )
        safe_print(
            f"[INFO] Resolved version_id: {summary['resolved_version_id']}/{summary['input_records']}"
        )
        safe_print(f"[INFO] Output written to: {summary['output_path']}")

        if not args.quiet_json:
            safe_print(json.dumps(summary, ensure_ascii=False, indent=2))

        return 0
    except IDResolutionError as exc:
        safe_print(f"[ID_RESOLUTION_ERROR] {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        safe_print(f"[UNEXPECTED_ERROR] {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
