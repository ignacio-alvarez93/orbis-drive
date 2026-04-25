from __future__ import annotations

import argparse
import json

from src.catalogo.concesionarios.id_resolution.orbis_location_bridge import OrbisLocationBridge
from src.catalogo.concesionarios.pipeline.ingestion_pipeline import ConcesionariosIngestionPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ejecuta el pipeline de ingestión de T_Concesionarios."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Ruta al JSON exploratorio unificado o de una fuente.",
    )
    parser.add_argument(
        "--db-path",
        required=True,
        help="Ruta a la base SQLite Orbis_Drive.db",
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Ruta de salida del reporte JSON.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    resolver = OrbisLocationBridge(args.db_path)
    pipeline = ConcesionariosIngestionPipeline(resolver)

    payload = pipeline.run(
        input_path=args.input,
        report_path=args.report,
    )

    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()