from __future__ import annotations

import argparse
from pathlib import Path

from src.catalogo.scraping.versiones.scraper_versiones import run_scraper


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ejecutor del scraper semimanual de versiones v3"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Ruta al CSV con URLs de versiones",
    )
    parser.add_argument(
        "--contract",
        type=str,
        required=True,
        help="Ruta al contrato JSON de T_Versiones",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Directorio de salida del scraper",
    )
    parser.add_argument(
        "--from-html",
        nargs="*",
        default=None,
        help="Lista de ficheros HTML locales para modo debug",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Número máximo de URLs a procesar cuando se usa --csv",
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="Página inicial a procesar en el CSV (base 1)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    html_files = args.from_html
    if html_files:
        expanded: list[str] = []
        for item in html_files:
            matches = list(Path().glob(item))
            if matches:
                expanded.extend(str(match) for match in matches)
            else:
                expanded.append(item)
        html_files = expanded

    run_scraper(
        csv_path=args.csv,
        contract_path=args.contract,
        output_dir=args.output_dir,
        html_files=html_files,
        limit=args.limit,
        start_page=args.start_page,
    )


if __name__ == "__main__":
    main()