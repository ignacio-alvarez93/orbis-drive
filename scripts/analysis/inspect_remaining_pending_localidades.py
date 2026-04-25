from __future__ import annotations

import argparse
import json
import re
import sqlite3
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


def normalize_cmp(value: str) -> str:
    value = value.strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace("’", "'").replace("`", "'")
    value = value.replace("'", " ")
    value = value.replace("-", " ")
    value = re.sub(r"[^\w\s/]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def load_report(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"No existe el reporte: {path}")
    return json.loads(p.read_text(encoding="utf-8"))


def extract_field(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1) if m else None


def load_localidades(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT
            l.id AS localidad_id,
            l.nombre AS localidad_nombre,
            l.codigo_postal AS codigo_postal,
            s.nombre AS subdivision_nombre
        FROM T_Localidades l
        LEFT JOIN T_Subdivisiones_Administrativas s
            ON s.id = l.subdivision_id
        """
    ).fetchall()
    return [dict(r) for r in rows]


def score_candidate(locality_norm: str, loc_name_norm: str) -> float:
    return SequenceMatcher(None, locality_norm, loc_name_norm).ratio()


def inspect_pending(pending: dict[str, Any], localidades: list[dict[str, Any]]) -> dict[str, Any]:
    warning = (pending.get("warnings") or [""])[0]

    locality = extract_field(r"localidad='([^']+)'", warning) or ""
    province = extract_field(r"provincia='([^']+)'", warning)
    cp = extract_field(r"cp='([^']+)'", warning) or pending.get("postal_code_raw")

    locality_norm = normalize_cmp(locality)
    province_norm = normalize_cmp(province) if province else None

    scored = []
    for loc in localidades:
        loc_name = loc["localidad_nombre"] or ""
        prov_name = loc["subdivision_nombre"] or ""

        loc_name_norm = normalize_cmp(loc_name)
        prov_name_norm = normalize_cmp(prov_name)

        ratio = score_candidate(locality_norm, loc_name_norm)

        province_bonus = 0.0
        if province_norm and prov_name_norm == province_norm:
            province_bonus = 0.15

        score = ratio + province_bonus

        scored.append({
            "score": round(score, 4),
            "localidad_id": loc["localidad_id"],
            "localidad_nombre": loc_name,
            "subdivision_nombre": prov_name,
            "codigo_postal": loc["codigo_postal"],
        })

    scored = sorted(scored, key=lambda x: x["score"], reverse=True)[:10]

    return {
        "source_name": pending.get("source_name"),
        "record_external_id": pending.get("record_external_id"),
        "dealer_name_raw": pending.get("dealer_name_raw"),
        "location_raw": pending.get("location_raw"),
        "postal_code_raw": pending.get("postal_code_raw"),
        "warning": warning,
        "parsed_locality": locality,
        "parsed_province": province,
        "parsed_cp": cp,
        "top_candidates": scored,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspección fina de pendientes contra T_Localidades."
    )
    parser.add_argument("--report", required=True)
    parser.add_argument("--db-path", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    report = load_report(args.report)
    pending_records = report.get("pending_records", [])

    with sqlite3.connect(args.db_path) as conn:
        localidades = load_localidades(conn)

    inspected = [inspect_pending(p, localidades) for p in pending_records]

    payload = {
        "pending_total": len(pending_records),
        "records": inspected,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "pending_total": len(pending_records),
        "output": str(out),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()