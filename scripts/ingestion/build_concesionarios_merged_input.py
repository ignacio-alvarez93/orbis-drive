from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"No existe: {path}")
    return json.loads(p.read_text(encoding="utf-8"))


def build_merged_payload(inputs: list[str]) -> dict[str, Any]:
    merged_records = []
    source_names = []
    source_urls = []

    for input_path in inputs:
        payload = load_json(input_path)

        source_name = payload.get("source_name", "")
        source_url = payload.get("source_url", "")
        scrape_date = payload.get("scrape_date", "")

        source_names.append(source_name)
        source_urls.append(source_url)

        for record in payload.get("records", []):
            enriched = dict(record)
            enriched["_merged_source_name"] = source_name
            enriched["_merged_source_url"] = source_url
            enriched["_merged_scrape_date"] = scrape_date
            merged_records.append(enriched)

    return {
        "source_name": "merged_concesionarios_sources",
        "source_url": "MULTI_SOURCE",
        "scrape_date": "",
        "merged_sources": [
            {"source_name": n, "source_url": u}
            for n, u in zip(source_names, source_urls)
        ],
        "records": merged_records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Une múltiples JSON exploratorios de concesionarios en un único lote."
    )
    parser.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="Lista de JSONs exploratorios de entrada.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Ruta de salida del JSON combinado.",
    )
    args = parser.parse_args()

    merged = build_merged_payload(args.inputs)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Merged file written to: {out}")
    print(f"Total records: {len(merged['records'])}")


if __name__ == "__main__":
    main()