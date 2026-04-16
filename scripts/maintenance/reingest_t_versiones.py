from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from src.catalogo.pipeline.ingestion_pipeline import TVersionesIngestionPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reingestión controlada de T_Versiones con backup, borrado selectivo por clave semántica y reingestión."
    )
    parser.add_argument("--db-path", required=True, help="Ruta a la base SQLite operativa.")
    parser.add_argument("--dataset", required=True, help="Ruta al dataset JSON resuelto con IDs.")
    parser.add_argument(
        "--backup-dir",
        default="db/local/backups",
        help="Directorio donde se guardará el backup de la DB.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="No genera backup antes de reingestar.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No borra ni inserta. Solo informa del impacto esperado.",
    )
    parser.add_argument(
        "--strict-batch",
        action="store_true",
        default=False,
        help="Si se activa, un fallo en una fila aborta toda la ingestión.",
    )
    parser.add_argument(
        "--report-path",
        default="data/samples/output/reingestion_report.json",
        help="Ruta donde guardar el informe JSON de la reingestión.",
    )
    return parser.parse_args()


def safe_print(message: str, *, file=None) -> None:
    target = file if file is not None else sys.stdout
    try:
        print(message, file=target)
    except UnicodeEncodeError:
        sanitized = message.encode("ascii", "replace").decode("ascii")
        print(sanitized, file=target)


def load_dataset(dataset_path: Path) -> list[dict]:
    rows = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("El dataset debe ser una lista JSON.")
    if not rows:
        raise ValueError("El dataset no puede estar vacío.")
    return rows


def collect_semantic_keys(rows: list[dict]) -> list[tuple[str, str, object, object]]:
    semantic_keys = []
    for index, row in enumerate(rows):
        version_name_canonical = row.get("version_name_canonical")
        generation_id = row.get("generation_id")
        production_start_year = row.get("production_start_year")
        production_end_year = row.get("production_end_year")

        if not version_name_canonical:
            raise ValueError(
                f"Fila {index}: falta 'version_name_canonical'."
            )
        if not generation_id:
            raise ValueError(
                f"Fila {index}: falta 'generation_id'. Ejecuta antes ID_RESOLUTION."
            )

        semantic_keys.append(
            (
                version_name_canonical,
                generation_id,
                production_start_year,
                production_end_year,
            )
        )
    return semantic_keys


def create_backup(db_path: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{db_path.stem}_backup_pre_reingestion_{timestamp}{db_path.suffix}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def count_existing_rows(conn: sqlite3.Connection, semantic_keys: list[tuple[str, str, object, object]]) -> int:
    total = 0
    for version_name_canonical, generation_id, production_start_year, production_end_year in semantic_keys:
        sql = '''
            SELECT COUNT(*)
            FROM T_Versiones
            WHERE version_name_canonical = ?
              AND generation_id = ?
              AND production_start_year IS ?
              AND production_end_year IS ?
        '''
        total += conn.execute(
            sql,
            (
                version_name_canonical,
                generation_id,
                production_start_year,
                production_end_year,
            ),
        ).fetchone()[0]
    return total


def delete_existing_rows(conn: sqlite3.Connection, semantic_keys: list[tuple[str, str, object, object]]) -> int:
    deleted = 0
    for version_name_canonical, generation_id, production_start_year, production_end_year in semantic_keys:
        sql = '''
            DELETE FROM T_Versiones
            WHERE version_name_canonical = ?
              AND generation_id = ?
              AND production_start_year IS ?
              AND production_end_year IS ?
        '''
        cur = conn.execute(
            sql,
            (
                version_name_canonical,
                generation_id,
                production_start_year,
                production_end_year,
            ),
        )
        deleted += cur.rowcount if cur.rowcount is not None and cur.rowcount >= 0 else 0
    return deleted


def main() -> int:
    args = parse_args()

    db_path = Path(args.db_path)
    dataset_path = Path(args.dataset)
    backup_dir = Path(args.backup_dir)
    report_path = Path(args.report_path)

    if not db_path.exists():
        safe_print(f"[REINGESTION_ERROR] No existe la base de datos: {db_path}", file=sys.stderr)
        return 2

    if not dataset_path.exists():
        safe_print(f"[REINGESTION_ERROR] No existe el dataset: {dataset_path}", file=sys.stderr)
        return 2

    rows = load_dataset(dataset_path)
    semantic_keys = collect_semantic_keys(rows)

    report: dict = {
        "status": "pending",
        "db_path": str(db_path),
        "dataset": str(dataset_path),
        "input_records": len(rows),
        "distinct_semantic_keys": len(set(semantic_keys)),
        "dry_run": args.dry_run,
        "backup_created": None,
        "existing_rows_matching_dataset": 0,
        "deleted_rows": 0,
        "deletion_mode": "semantic_key",
        "ingestion_report": None,
    }

    if not args.no_backup:
        backup_path = create_backup(db_path, backup_dir)
        report["backup_created"] = str(backup_path)
        safe_print(f"[INFO] Backup created: {backup_path}")

    conn = sqlite3.connect(db_path)

    try:
        existing_rows = count_existing_rows(conn, semantic_keys)
        report["existing_rows_matching_dataset"] = existing_rows

        safe_print(f"[INFO] Dataset rows: {len(rows)}")
        safe_print(f"[INFO] Distinct semantic keys in dataset: {len(set(semantic_keys))}")
        safe_print(f"[INFO] Existing rows matching dataset in DB: {existing_rows}")
        safe_print("[INFO] Deletion mode: semantic_key")

        if args.dry_run:
            report["status"] = "dry_run"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            safe_print(f"[INFO] Dry run completed. Report written to: {report_path}")
            safe_print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0

        conn.execute("BEGIN")
        deleted_rows = delete_existing_rows(conn, semantic_keys)
        report["deleted_rows"] = deleted_rows
        safe_print(f"[INFO] Deleted rows from T_Versiones: {deleted_rows}")

        pipeline = TVersionesIngestionPipeline(
            conn=conn,
            strict_batch=args.strict_batch,
        )
        ingestion_report = pipeline.run(str(dataset_path))

        report["ingestion_report"] = ingestion_report.to_dict()
        report["status"] = "ok"

        conn.commit()

        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

        safe_print("[INFO] Reingestion completed successfully.")
        safe_print(f"[INFO] Report written to: {report_path}")
        safe_print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    except Exception as exc:
        conn.rollback()
        report["status"] = "failed"
        report["error"] = str(exc)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        safe_print(f"[REINGESTION_ERROR] {exc}", file=sys.stderr)
        safe_print(f"[INFO] Failure report written to: {report_path}", file=sys.stderr)
        return 2

    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
