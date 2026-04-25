from __future__ import annotations

import argparse
import json
import sqlite3
import unicodedata
import re
from difflib import get_close_matches
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


def load_localidades(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT
            l.id AS localidad_id,
            l.nombre AS localidad_nombre,
            l.codigo_postal AS codigo_postal,
            l.subdivision_id AS subdivision_id,
            s.nombre AS subdivision_nombre,
            p.codigo_iso AS country_iso
        FROM T_Localidades l
        LEFT JOIN T_Subdivisiones_Administrativas s
            ON s.id = l.subdivision_id
        LEFT JOIN T_Paises p
            ON p.id = l.pais_id
        """
    ).fetchall()

    return [dict(r) for r in rows]


def extract_localidad_from_warning(warning: str) -> str | None:
    m = re.search(r"localidad='([^']+)'", warning)
    return m.group(1) if m else None


def extract_provincia_from_warning(warning: str) -> str | None:
    m = re.search(r"provincia='([^']+)'", warning)
    return m.group(1) if m else None


def extract_cp_from_warning(warning: str) -> str | None:
    m = re.search(r"cp='([^']+)'", warning)
    return m.group(1) if m else None


def reconcile_pending_record(
    pending: dict[str, Any],
    localidades: list[dict[str, Any]],
) -> dict[str, Any]:
    warnings = pending.get("warnings", [])
    warning_text = warnings[0] if warnings else ""

    locality_candidate = extract_localidad_from_warning(warning_text) or pending.get("location_raw") or ""
    province_candidate = extract_provincia_from_warning(warning_text)
    postal_code_candidate = extract_cp_from_warning(warning_text) or pending.get("postal_code_raw")

    locality_norm = normalize_cmp(locality_candidate)
    province_norm = normalize_cmp(province_candidate) if province_candidate else None
    cp_norm = str(postal_code_candidate).zfill(5) if postal_code_candidate and str(postal_code_candidate).isdigit() else postal_code_candidate

    exact_matches = []
    province_matches = []
    cp_matches = []

    for loc in localidades:
        loc_name_norm = normalize_cmp(loc["localidad_nombre"] or "")
        prov_name_norm = normalize_cmp(loc["subdivision_nombre"] or "")

        if locality_norm and loc_name_norm == locality_norm:
            exact_matches.append(loc)

        if locality_norm and province_norm:
            if loc_name_norm == locality_norm and prov_name_norm == province_norm:
                province_matches.append(loc)

        loc_cp = loc.get("codigo_postal")
        if cp_norm and loc_cp and str(loc_cp).strip() == str(cp_norm).strip():
            cp_matches.append(loc)

    normalized_names = sorted({normalize_cmp(loc["localidad_nombre"] or ""): loc["localidad_nombre"] for loc in localidades}.items())
    candidate_name_map = {norm: original for norm, original in normalized_names}
    close_norms = get_close_matches(locality_norm, list(candidate_name_map.keys()), n=8, cutoff=0.72)
    close_matches = [candidate_name_map[n] for n in close_norms]

    return {
        "source_name": pending.get("source_name"),
        "record_external_id": pending.get("record_external_id"),
        "dealer_name_raw": pending.get("dealer_name_raw"),
        "location_raw": pending.get("location_raw"),
        "postal_code_raw": pending.get("postal_code_raw"),
        "warning": warning_text,
        "parsed_locality_candidate": locality_candidate,
        "parsed_province_candidate": province_candidate,
        "parsed_postal_code_candidate": postal_code_candidate,
        "exact_matches_count": len(exact_matches),
        "province_matches_count": len(province_matches),
        "cp_matches_count": len(cp_matches),
        "exact_matches": [
            {
                "localidad_id": x["localidad_id"],
                "localidad_nombre": x["localidad_nombre"],
                "subdivision_nombre": x["subdivision_nombre"],
                "codigo_postal": x["codigo_postal"],
            }
            for x in exact_matches[:10]
        ],
        "province_matches": [
            {
                "localidad_id": x["localidad_id"],
                "localidad_nombre": x["localidad_nombre"],
                "subdivision_nombre": x["subdivision_nombre"],
                "codigo_postal": x["codigo_postal"],
            }
            for x in province_matches[:10]
        ],
        "cp_matches": [
            {
                "localidad_id": x["localidad_id"],
                "localidad_nombre": x["localidad_nombre"],
                "subdivision_nombre": x["subdivision_nombre"],
                "codigo_postal": x["codigo_postal"],
            }
            for x in cp_matches[:10]
        ],
        "close_name_candidates": close_matches,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reconciliación de pendientes de concesionarios contra T_Localidades."
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Ruta al reporte del pipeline combinado.",
    )
    parser.add_argument(
        "--db-path",
        required=True,
        help="Ruta a Orbis_Drive.db",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Ruta de salida JSON de reconciliación.",
    )
    args = parser.parse_args()

    report = load_report(args.report)
    pending_records = report.get("pending_records", [])

    with sqlite3.connect(args.db_path) as conn:
        localidades = load_localidades(conn)

    reconciled = [reconcile_pending_record(item, localidades) for item in pending_records]

    payload = {
        "pending_total": len(pending_records),
        "reconciled_total": len(reconciled),
        "records": reconciled,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "pending_total": len(pending_records),
        "reconciled_total": len(reconciled),
        "output": str(out),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()