
from __future__ import annotations

import argparse
import json
import sys

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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = resolve_dataset_file(
            db_path=args.db_path,
            input_path=args.input,
            output_path=args.output,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except IDResolutionError as exc:
        print(f"[ID_RESOLUTION_ERROR] {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[UNEXPECTED_ERROR] {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
