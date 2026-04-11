from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from src.catalogo.pipeline.ingestion_pipeline import TVersionesPilotIngestionPipeline


class TVersionesIngestionPipeline(TVersionesPilotIngestionPipeline):
    """
    Variante no piloto:
    - acepta lotes de cualquier tamaño
    - mantiene el resto del comportamiento igual
    """

    def _load_rows(self, dataset_path: str) -> list[dict]:
        dataset_file = Path(dataset_path)
        rows = json.loads(dataset_file.read_text(encoding="utf-8"))

        if not isinstance(rows, list):
            raise ValueError("El dataset de ingestión debe ser una lista JSON.")

        if len(rows) == 0:
            raise ValueError("El dataset de ingestión no puede estar vacío.")

        for row in rows:
            row["_source_dataset"] = str(dataset_file)

        return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingestión real de T_Versiones (sin límite de tamaño de lote)."
    )
    parser.add_argument(
        "--db-path",
        required=True,
        help="Ruta a la base de datos SQLite.",
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Ruta al dataset JSON resuelto para ingestión.",
    )
    parser.add_argument(
        "--strict-batch",
        action="store_true",
        default=False,
        help="Si se activa, un fallo en una fila aborta toda la ingestión.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    db_path = Path(args.db_path)
    dataset_path = Path(args.dataset)

    if not db_path.exists():
        print(f"[INGESTION_ERROR] No existe la base de datos: {db_path}", file=sys.stderr)
        return 2

    if not dataset_path.exists():
        print(f"[INGESTION_ERROR] No existe el dataset: {dataset_path}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(db_path)

    try:
        pipeline = TVersionesIngestionPipeline(
            conn=conn,
            strict_batch=args.strict_batch,
        )
        report = pipeline.run(str(dataset_path))
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"[INGESTION_ERROR] {exc}", file=sys.stderr)
        return 2
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
