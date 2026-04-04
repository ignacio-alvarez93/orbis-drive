from __future__ import annotations

import argparse
import json
import sqlite3
import sys

from src.catalogo.pipeline.ingestion_pipeline import (
    PilotIngestionError,
    TVersionesPilotIngestionPipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta la ingestión piloto controlada de T_Versiones"
    )
    parser.add_argument("--db-path", required=True, help="Ruta a la base de datos SQLite")
    parser.add_argument("--dataset", required=True, help="Ruta al dataset ya validado")
    parser.add_argument(
        "--non-strict",
        action="store_true",
        help="No hacer rollback completo del lote ante el primer fallo",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    conn = sqlite3.connect(args.db_path)
    conn.row_factory = sqlite3.Row

    pipeline = TVersionesPilotIngestionPipeline(
        conn=conn,
        strict_batch=not args.non_strict,
    )

    try:
        report = pipeline.run(args.dataset)
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 0
    except PilotIngestionError as exc:
        print(f"[INGESTION_ERROR] {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[UNEXPECTED_ERROR] {exc}", file=sys.stderr)
        return 3
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
