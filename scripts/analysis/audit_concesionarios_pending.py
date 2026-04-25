from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_report(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"No existe el reporte: {path}")
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audita pendientes del pipeline de T_Concesionarios."
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Ruta al JSON de reporte del pipeline.",
    )
    parser.add_argument(
        "--output",
        required=False,
        help="Ruta opcional para guardar auditoría en JSON.",
    )
    args = parser.parse_args()

    report = load_report(args.report)
    pending_records = report.get("pending_records", [])

    by_source = Counter()
    by_location = Counter()
    by_postal_code = Counter()
    by_warning = Counter()

    for item in pending_records:
        by_source[item.get("source_name") or ""] += 1
        by_location[item.get("location_raw") or ""] += 1
        by_postal_code[item.get("postal_code_raw") or ""] += 1

        for warning in item.get("warnings", []):
            by_warning[warning] += 1

    audit = {
        "pending_total": len(pending_records),
        "top_sources": by_source.most_common(20),
        "top_locations": by_location.most_common(50),
        "top_postal_codes": by_postal_code.most_common(50),
        "top_warnings": by_warning.most_common(50),
    }

    print(json.dumps(audit, ensure_ascii=False, indent=2))

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()