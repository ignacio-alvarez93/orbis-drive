from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class RowOutcome:
    row_number: int
    generation_id: str
    generation_name: str
    action: str
    reason: str


@dataclass
class Summary:
    csv_path: str
    db_path: str
    processed: int
    inserted: int
    skipped_duplicates: int
    skipped_existing: int
    failed: int
    timestamp_utc: str


REQUIRED_HEADERS = {
    "manufacturer_id",
    "manufacturer_name",
    "model_id",
    "model_name",
    "generation_id",
    "generation_name",
    "generation_name_canonical",
}


class IngestionError(Exception):
    pass


def info(message: str) -> None:
    print(f"[INFO] {message}")


def warn(message: str) -> None:
    print(f"[WARN] {message}")


def error(message: str) -> None:
    print(f"[ERROR] {message}")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_file(path: Path, label: str) -> None:
    if not path.exists():
        raise IngestionError(f"No existe {label}: {path}")


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split()).strip()


def load_rows(csv_path: Path) -> list[dict[str, str]]:
    ensure_file(csv_path, "CSV de generaciones")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])
        missing = REQUIRED_HEADERS - headers
        if missing:
            raise IngestionError(
                "CSV de generaciones inválido. Faltan cabeceras: " + ", ".join(sorted(missing))
            )
        rows = []
        for raw in reader:
            row = {k: normalize_text(v) for k, v in raw.items()}
            if not any(row.values()):
                continue
            rows.append(row)

    if not rows:
        raise IngestionError("El CSV no contiene filas útiles.")

    return rows


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cur.fetchone() is not None


def load_model_lookup(conn: sqlite3.Connection) -> dict[str, dict[str, str]]:
    if not table_exists(conn, "T_Modelos"):
        raise IngestionError("La base no contiene la tabla T_Modelos.")

    cur = conn.execute(
        """
        SELECT manufacturer_id, manufacturer_name, model_id, model_name,
               model_href_relative, model_href_absolute
        FROM T_Modelos
        """
    )
    lookup: dict[str, dict[str, str]] = {}
    for row in cur.fetchall():
        entry = {
            "manufacturer_id": normalize_text(row[0]),
            "manufacturer_name": normalize_text(row[1]),
            "model_id": normalize_text(row[2]),
            "model_name": normalize_text(row[3]),
            "model_href_relative": normalize_text(row[4]),
            "model_href_absolute": normalize_text(row[5]),
        }
        lookup[entry["model_id"]] = entry
    return lookup


def load_existing_generations(conn: sqlite3.Connection) -> tuple[set[str], set[tuple[str, str]]]:
    if not table_exists(conn, "T_Generaciones"):
        raise IngestionError("La base no contiene la tabla T_Generaciones.")

    cur = conn.execute(
        "SELECT generation_id, model_id, generation_name FROM T_Generaciones"
    )
    existing_ids: set[str] = set()
    existing_pairs: set[tuple[str, str]] = set()
    for generation_id, model_id, generation_name in cur.fetchall():
        generation_id = normalize_text(generation_id)
        model_id = normalize_text(model_id)
        generation_name = normalize_text(generation_name)
        if generation_id:
            existing_ids.add(generation_id)
        if model_id and generation_name:
            existing_pairs.add((model_id, generation_name))
    return existing_ids, existing_pairs


def parse_nullable_int(value: str) -> int | None:
    value = normalize_text(value)
    if not value:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise IngestionError(f"No se puede convertir a entero: {value}") from exc


def validate_row(row_number: int, row: dict[str, str], model_lookup: dict[str, dict[str, str]]) -> None:
    for key in sorted(REQUIRED_HEADERS):
        if not normalize_text(row.get(key, "")):
            raise IngestionError(f"Fila {row_number}: campo obligatorio vacío: {key}")

    model_id = row["model_id"]
    manufacturer_id = row["manufacturer_id"]
    model_name = row["model_name"]
    manufacturer_name = row["manufacturer_name"]

    model_db = model_lookup.get(model_id)
    if model_db is None:
        raise IngestionError(
            f"Fila {row_number}: model_id inexistente en T_Modelos: {model_id}"
        )

    if manufacturer_id != model_db["manufacturer_id"]:
        raise IngestionError(
            f"Fila {row_number}: manufacturer_id no coincide con T_Modelos para model_id={model_id}"
        )

    if normalize_text(manufacturer_name).upper() != normalize_text(model_db["manufacturer_name"]).upper():
        raise IngestionError(
            f"Fila {row_number}: manufacturer_name no coincide con T_Modelos para model_id={model_id}"
        )

    if normalize_text(model_name).upper() != normalize_text(model_db["model_name"]).upper():
        raise IngestionError(
            f"Fila {row_number}: model_name no coincide con T_Modelos para model_id={model_id}"
        )


INSERT_SQL = """
INSERT INTO T_Generaciones (
    manufacturer_id,
    manufacturer_name,
    manufacturer_name_upper,
    model_id,
    model_name,
    model_name_upper,
    generation_id,
    generation_name,
    generation_name_canonical,
    generation_name_upper,
    year_start,
    year_end,
    year_end_raw,
    generation_href_relative,
    generation_href_absolute
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def ingest_generations(
    db_path: Path,
    csv_path: Path,
    dry_run: bool = False,
) -> tuple[Summary, list[RowOutcome]]:
    rows = load_rows(csv_path)
    outcomes: list[RowOutcome] = []

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        model_lookup = load_model_lookup(conn)
        existing_ids, existing_pairs = load_existing_generations(conn)

        seen_csv_ids: set[str] = set()
        seen_csv_pairs: set[tuple[str, str]] = set()

        processed = 0
        inserted = 0
        skipped_duplicates = 0
        skipped_existing = 0
        failed = 0

        for index, row in enumerate(rows, start=2):
            processed += 1
            generation_id = normalize_text(row.get("generation_id"))
            generation_name = normalize_text(row.get("generation_name"))
            model_id = normalize_text(row.get("model_id"))
            pair = (model_id, generation_name)

            try:
                validate_row(index, row, model_lookup)

                if generation_id in seen_csv_ids or pair in seen_csv_pairs:
                    skipped_duplicates += 1
                    outcomes.append(
                        RowOutcome(index, generation_id, generation_name, "skipped_duplicate_csv", "Duplicado dentro del CSV")
                    )
                    continue

                seen_csv_ids.add(generation_id)
                seen_csv_pairs.add(pair)

                if generation_id in existing_ids or pair in existing_pairs:
                    skipped_existing += 1
                    outcomes.append(
                        RowOutcome(index, generation_id, generation_name, "skipped_existing_db", "La generación ya existe en DB")
                    )
                    continue

                payload = (
                    row["manufacturer_id"],
                    row["manufacturer_name"],
                    normalize_text(row.get("manufacturer_name_upper")) or row["manufacturer_name"].upper(),
                    row["model_id"],
                    row["model_name"],
                    normalize_text(row.get("model_name_upper")) or row["model_name"].upper(),
                    row["generation_id"],
                    row["generation_name"],
                    row["generation_name_canonical"],
                    normalize_text(row.get("generation_name_upper")) or row["generation_name_canonical"].upper(),
                    parse_nullable_int(row.get("year_start", "")),
                    normalize_text(row.get("year_end", "")) or None,
                    normalize_text(row.get("year_end_raw", "")) or None,
                    normalize_text(row.get("generation_href_relative", "")) or None,
                    normalize_text(row.get("generation_href_absolute", "")) or None,
                )

                if not dry_run:
                    conn.execute(INSERT_SQL, payload)
                inserted += 1
                outcomes.append(
                    RowOutcome(index, generation_id, generation_name, "inserted", "OK")
                )
                existing_ids.add(generation_id)
                existing_pairs.add(pair)

            except Exception as exc:
                failed += 1
                outcomes.append(
                    RowOutcome(index, generation_id, generation_name, "failed", str(exc))
                )

        if dry_run:
            conn.rollback()
        else:
            conn.commit()

    finally:
        conn.close()

    summary = Summary(
        csv_path=str(csv_path),
        db_path=str(db_path),
        processed=processed,
        inserted=inserted,
        skipped_duplicates=skipped_duplicates,
        skipped_existing=skipped_existing,
        failed=failed,
        timestamp_utc=now_utc(),
    )
    return summary, outcomes


def write_report(path: Path, summary: Summary, outcomes: list[RowOutcome]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": asdict(summary),
        "rows": [asdict(item) for item in outcomes],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingresa generaciones desde un CSV a T_Generaciones"
    )
    parser.add_argument("--db-path", required=True, help="Ruta a la base SQLite")
    parser.add_argument("--csv", required=True, help="Ruta al CSV de generaciones")
    parser.add_argument(
        "--report",
        help="Ruta opcional para guardar informe JSON",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida todo pero no escribe en DB",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    db_path = Path(args.db_path).expanduser()
    csv_path = Path(args.csv).expanduser()

    try:
        ensure_file(db_path, "base de datos")
        summary, outcomes = ingest_generations(
            db_path=db_path,
            csv_path=csv_path,
            dry_run=args.dry_run,
        )

        info(f"Processed: {summary.processed}")
        info(f"Inserted: {summary.inserted}")
        info(f"Skipped duplicates in CSV: {summary.skipped_duplicates}")
        info(f"Skipped existing in DB: {summary.skipped_existing}")
        info(f"Failed: {summary.failed}")
        if args.dry_run:
            warn("Dry run activo: no se han escrito cambios en DB.")

        failures = [o for o in outcomes if o.action == "failed"]
        if failures:
            error("Filas fallidas:")
            for item in failures[:20]:
                print(f"  - fila {item.row_number}: {item.reason}")
            if len(failures) > 20:
                print(f"  ... y {len(failures) - 20} más")

        if args.report:
            report_path = Path(args.report).expanduser()
            write_report(report_path, summary, outcomes)
            info(f"Informe guardado en: {report_path}")

        return 0 if summary.failed == 0 else 1

    except IngestionError as exc:
        error(str(exc))
        return 2
    except sqlite3.IntegrityError as exc:
        error(f"Error de integridad SQLite: {exc}")
        return 3
    except Exception as exc:
        error(f"Fallo inesperado: {exc}")
        return 99


if __name__ == "__main__":
    sys.exit(main())
