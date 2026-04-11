from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def norm(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().upper().split())


def source_semantic_key(row: dict[str, Any]) -> str:
    return "|".join(
        [
            norm(row.get("generation_id")),
            norm(row.get("version_name_canonical")),
        ]
    )


def enriched_identity(row: dict[str, Any]) -> str:
    return "|".join(
        [
            norm(row.get("generation_id")),
            norm(row.get("version_name_canonical")),
            norm(row.get("production_start_year")),
            norm(row.get("production_end_year")),
            norm(row.get("power_cv")),
            norm(row.get("fuel_type")),
        ]
    )


def summarize_variants(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    variants: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = enriched_identity(row)
        variants[key] = {
            "generation_id": row.get("generation_id"),
            "version_name": row.get("version_name"),
            "version_name_canonical": row.get("version_name_canonical"),
            "production_start_year": row.get("production_start_year"),
            "production_end_year": row.get("production_end_year"),
            "power_cv": row.get("power_cv"),
            "fuel_type": row.get("fuel_type"),
            "source_version_url": row.get("source_version_url"),
        }
    return list(variants.values())


def classify_group(rows: list[dict[str, Any]]) -> str:
    identities = {enriched_identity(r) for r in rows}
    if len(identities) <= 1:
        return "duplicado_real"
    return "duplicado_aparente_revisar"


def build_report(dataset_rows: list[dict[str, Any]], ingestion_report: dict[str, Any]) -> dict[str, Any]:
    by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in dataset_rows:
        by_key[source_semantic_key(row)].append(row)

    skipped_records = [
        r for r in ingestion_report.get("records", [])
        if r.get("status") == "skipped_duplicate"
    ]

    groups = []
    for rec in skipped_records:
        semantic_key = rec.get("semantic_key", "")
        parts = semantic_key.split("|")
        if len(parts) >= 2:
            version_name_canonical = parts[0]
            generation_id = parts[1]
            key = "|".join([norm(generation_id), norm(version_name_canonical)])
        else:
            key = None

        source_rows = by_key.get(key, []) if key else []
        classification = classify_group(source_rows) if source_rows else "sin_fuente_localizada"

        groups.append(
            {
                "semantic_key": semantic_key,
                "classification": classification,
                "skip_message": rec.get("message"),
                "record_ref": rec.get("record_ref", {}),
                "source_records_count": len(source_rows),
                "source_variants": summarize_variants(source_rows),
            }
        )

    return {
        "processed": ingestion_report.get("processed"),
        "inserted": ingestion_report.get("inserted"),
        "skipped_duplicates": ingestion_report.get("skipped_duplicates"),
        "failed": ingestion_report.get("failed"),
        "duplicate_groups_review": groups,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audita skipped_duplicates tras ingestión de T_Versiones."
    )
    parser.add_argument("--dataset", required=True, help="JSON resuelto o clean usado para ingestión.")
    parser.add_argument("--ingestion-report", required=True, help="JSON de salida de la ingestión.")
    parser.add_argument("--output", required=True, help="Ruta del JSON de auditoría.")
    args = parser.parse_args()

    dataset_rows = load_json(args.dataset)
    report = load_json(args.ingestion_report)

    if not isinstance(dataset_rows, list):
        raise ValueError("El dataset debe ser una lista JSON.")
    if not isinstance(report, dict):
        raise ValueError("El ingestion-report debe ser un objeto JSON.")

    output = build_report(dataset_rows, report)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Auditoría generada: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
