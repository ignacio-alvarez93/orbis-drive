from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin
import unicodedata

from bs4 import BeautifulSoup

try:
    from seleniumbase import sb_cdp
except Exception:
    sb_cdp = None


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = REPO_ROOT / "contracts" / "catalogo" / "t_versiones.contract.json"
DEFAULT_DB = REPO_ROOT / "db" / "local" / "Orbis_Drive.db"
DEFAULT_OUTPUT_BASE = REPO_ROOT / "data" / "samples" / "output"
DEFAULT_INPUT_BASE = REPO_ROOT / "data" / "samples" / "input"
TRUTH_BASE = REPO_ROOT / "data" / "truth" / "catalogo"
VERSIONES_BASE = TRUTH_BASE / "versiones"
PENDING_DIR = REPO_ROOT / "data" / "catalogo_pendientes"
MODEL_REGISTRY = TRUTH_BASE / "model_registry.json"
BASE_URL = "https://www.encycarpedia.com/es/"

VALIDATION_RUNNER = REPO_ROOT / "scripts" / "validation" / "run_iig_catalogo.py"
CLASSIFY_DVL_RUNNER = REPO_ROOT / "scripts" / "validation" / "classify_dvl_results.py"
BATCH_MARK_RUNNER = REPO_ROOT / "scripts" / "validation" / "mark_batch_passed.py"
LOTE_RUNNER = REPO_ROOT / "scripts" / "validation" / "run_lote_validation.py"
SCRAPER_RUNNER = REPO_ROOT / "scripts" / "scraping" / "run_scraper_versiones.py"
ID_RESOLUTION_RUNNER = REPO_ROOT / "scripts" / "ingestion" / "run_t_versiones_id_resolution.py"
INGESTION_RUNNER = REPO_ROOT / "scripts" / "ingestion" / "run_t_versiones_ingestion.py"

CONCESIONARIOS_BASE = REPO_ROOT / "data" / "external" / "concesionarios"
CONCESIONARIOS_SAMPLE_BASE = REPO_ROOT / "data" / "samples" / "concesionarios"

CONCESIONARIOS_BUILD_MERGED_RUNNER = REPO_ROOT / "scripts" / "ingestion" / "build_concesionarios_merged_input.py"
CONCESIONARIOS_PIPELINE_RUNNER = REPO_ROOT / "scripts" / "ingestion" / "run_t_concesionarios_ingestion.py"
CONCESIONARIOS_DB_INGESTION_RUNNER = REPO_ROOT / "scripts" / "ingestion" / "run_t_concesionarios_db_ingestion.py"
CONCESIONARIOS_AUDIT_PENDING_RUNNER = REPO_ROOT / "scripts" / "analysis" / "audit_concesionarios_pending.py"
@dataclass
class StepResult:
    name: str
    ok: bool
    returncode: int
    stdout: str
    stderr: str
    command: list[str]


class OrbisError(Exception):
    pass


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repair_mojibake(value: str) -> str:
    """
    Intenta reparar casos típicos de texto UTF-8 mal decodificado como latin1/cp1252.
    Ejemplo: "LeÃ³n" -> "León".
    """
    if not value:
        return ""
    suspicious_markers = ("Ã", "Â", "Ð", "Ò", "Ó", "€", "™")
    if any(marker in value for marker in suspicious_markers):
        for encoding in ("latin1", "cp1252"):
            try:
                repaired = value.encode(encoding).decode("utf-8")
                if repaired:
                    return repaired
            except Exception:
                pass
    return value


def slugify(value: str) -> str:
    value = repair_mojibake(clean_text(value))
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    safe = re.sub(r"[^a-zA-Z0-9]+", "_", normalized.lower())
    safe = re.sub(r"_+", "_", safe)
    return safe.strip("_")


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(repair_mojibake(str(value)).split()).strip()


def prompt(text: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{text}{suffix}: ").strip()
    return value or (default or "")


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def phase(message: str, *, clear: bool = True) -> None:
    if clear:
        clear_screen()
    print(f"\n=== {message} ===")


def info(message: str) -> None:
    print(f"[INFO] {message}")


def warn(message: str) -> None:
    print(f"[WARN] {message}")


def error(message: str) -> None:
    print(f"[ERROR] {message}")


def ensure_file(path: Path, label: str) -> None:
    if not path.exists():
        raise OrbisError(f"No existe {label}: {path}")


def pause(message: str = "Pulsa ENTER para continuar...") -> None:
    try:
        input(message)
    except EOFError:
        pass


def get_page_source_to_file(default_url: str = "", output_path: Path | None = None) -> Path:
    if sb_cdp is None:
        raise OrbisError("No está disponible seleniumbase/sb_cdp para capturar HTML.")

    url = prompt("Escribe URL", default_url)
    if not url:
        raise OrbisError("Debes indicar una URL.")

    target = Path(prompt("Ruta salida HTML", str(output_path) if output_path else "coche.txt")).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)

    browser = sb_cdp.Chrome(url, uc=True)
    print(f"Página abierta: {url}")
    input("Pulsa ENTER cuando la página esté lista para capturar el HTML... ")
    html = browser.get_page_source()
    try:
        browser.quit()
    except Exception:
        pass

    target.write_text(html, encoding="utf-8")
    info(f"HTML guardado en: {target}")
    return target


def build_output_dir(label: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = DEFAULT_OUTPUT_BASE / f"{label}_{stamp}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_id(*parts: str) -> str:
    raw = "|".join(clean_text(p).lower() for p in parts)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def relative_to_repo(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve()))
    except Exception:
        return str(path)


def path_from_registry(value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def load_registry() -> list[dict[str, Any]]:
    if not MODEL_REGISTRY.exists():
        return []
    data = json.loads(MODEL_REGISTRY.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def save_registry(rows: list[dict[str, Any]]) -> None:
    MODEL_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(rows, key=lambda r: (r.get("manufacturer_slug", ""), r.get("model_slug", "")))
    MODEL_REGISTRY.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")


def get_registry_entry(manufacturer_slug: str, model_slug: str) -> dict[str, Any] | None:
    for row in load_registry():
        if row.get("manufacturer_slug") == manufacturer_slug and row.get("model_slug") == model_slug:
            return row
    return None


def upsert_registry_entry(entry: dict[str, Any]) -> dict[str, Any]:
    registry = load_registry()
    registry = [
        row
        for row in registry
        if not (
            row.get("manufacturer_slug") == entry.get("manufacturer_slug")
            and row.get("model_slug") == entry.get("model_slug")
        )
    ]
    registry.append(entry)
    save_registry(registry)
    return entry


def model_truth_dir(manufacturer: str, model: str) -> Path:
    return VERSIONES_BASE / slugify(manufacturer) / slugify(model)


def select_registered_model(require_generations: bool = False, require_links: bool = False) -> dict[str, Any]:
    registry = load_registry()
    if not registry:
        raise OrbisError("No hay modelos registrados.")

    phase("SELECCIONAR MODELO")
    ordered = sorted(registry, key=lambda r: (r.get("manufacturer_slug", ""), r.get("model_slug", "")))
    for idx, row in enumerate(ordered, start=1):
        extra = []
        if row.get("generations_csv_path"):
            extra.append("generaciones")
        if row.get("links_csv_path"):
            extra.append("links")
        if row.get("status"):
            extra.append(row["status"])
        extra_text = f" [{' | '.join(extra)}]" if extra else ""
        print(f"{idx}. {row['manufacturer_name']} {row['model_name']}{extra_text}")

    raw = prompt("Selecciona modelo por número")
    try:
        entry = ordered[int(raw) - 1]
    except Exception as exc:
        raise OrbisError("Selección inválida.") from exc

    if require_generations and not entry.get("generations_csv_path"):
        raise OrbisError("El modelo no tiene CSV de generaciones registrado.")
    if require_links and not entry.get("links_csv_path"):
        raise OrbisError("El modelo no tiene CSV de links registrado.")
    return entry


# ---------------------------------------------------------------------------
# CSV / HTML helpers
# ---------------------------------------------------------------------------

def read_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    ensure_file(csv_path, "CSV")
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def write_csv_rows(output_path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def first_non_empty(row: dict[str, Any], keys: Iterable[str]) -> str:
    for key in keys:
        value = clean_text(row.get(key))
        if value:
            return value
    return ""


def canonicalize_model_name(raw_name: str) -> str:
    name = clean_text(raw_name)
    name = re.sub(r"\(.*?\)", "", name)
    name = clean_text(name)
    suffixes = {"SC", "ST", "CUPRA", "FR", "SPORT", "GT", "TSI", "TDI"}
    tokens = [t for t in name.split() if t.upper() not in suffixes]
    return clean_text(tokens[0] if tokens else name)


def parse_generation_years(generation_name: str) -> tuple[int | None, int | None, str | None]:
    name = clean_text(generation_name)
    m = re.search(r"\((\d{4})-(actualidad|\d{4})\)", name, re.IGNORECASE)
    if not m:
        return None, None, None
    start = int(m.group(1))
    end_raw = m.group(2)
    if end_raw.lower() == "actualidad":
        return start, None, "actualidad"
    return start, int(end_raw), end_raw


def parse_models_html(html: str, manufacturer_name: str, manufacturer_href_relative: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    manufacturer_name = clean_text(manufacturer_name)
    manufacturer_href_relative = clean_text(manufacturer_href_relative).strip("/") + "/"
    manufacturer_id = generate_id(manufacturer_name, manufacturer_href_relative)

    for a in soup.select("div.mw > a.mb[href]"):
        href_relative = clean_text(a.get("href", ""))
        if not href_relative or href_relative.startswith("search?"):
            continue
        if not href_relative.startswith(manufacturer_href_relative):
            continue
        if href_relative == manufacturer_href_relative:
            continue

        strong = a.select_one("strong")
        raw_model_name = clean_text(strong.get_text(" ", strip=True) if strong else "")
        model_name = canonicalize_model_name(raw_model_name)
        if not model_name:
            continue

        model_id = generate_id(manufacturer_name, model_name)
        if model_id in seen:
            continue
        seen.add(model_id)

        rows.append(
            {
                "manufacturer_id": manufacturer_id,
                "manufacturer_name": manufacturer_name,
                "manufacturer_name_upper": manufacturer_name.upper(),
                "model_id": model_id,
                "model_name": model_name,
                "model_name_upper": model_name.upper(),
                "model_href_relative": href_relative,
                "model_href_absolute": urljoin(BASE_URL, href_relative),
            }
        )

    return rows


def parse_generations_html(
    html: str,
    manufacturer_name: str,
    manufacturer_href_relative: str,
    model_name: str,
) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    manufacturer_name = clean_text(manufacturer_name)
    model_name = clean_text(model_name)
    manufacturer_href_relative = clean_text(manufacturer_href_relative).strip("/") + "/"
    manufacturer_id = generate_id(manufacturer_name, manufacturer_href_relative)
    model_id = generate_id(manufacturer_name, model_name)

    for a in soup.select("div.mw > a.mb[href]"):
        href_relative = clean_text(a.get("href", ""))
        if not href_relative or href_relative.startswith("search?"):
            continue
        if not href_relative.startswith(manufacturer_href_relative):
            continue

        strong = a.select_one("strong")
        generation_name = clean_text(strong.get_text(" ", strip=True) if strong else "")
        if not generation_name:
            continue

        year_start, year_end, year_end_raw = parse_generation_years(generation_name)
        generation_name_canonical = (
            f"{model_name} {year_start}-{year_end_raw}"
            if year_start is not None and year_end_raw is not None
            else model_name
        )
        generation_id = generate_id(manufacturer_name, model_name, generation_name_canonical)
        if generation_id in seen:
            continue
        seen.add(generation_id)

        rows.append(
            {
                "manufacturer_id": manufacturer_id,
                "manufacturer_name": manufacturer_name,
                "manufacturer_name_upper": manufacturer_name.upper(),
                "model_id": model_id,
                "model_name": model_name,
                "model_name_upper": model_name.upper(),
                "generation_id": generation_id,
                "generation_name": generation_name,
                "generation_name_canonical": generation_name_canonical,
                "generation_name_upper": generation_name_canonical.upper(),
                "year_start": year_start,
                "year_end": year_end,
                "year_end_raw": year_end_raw,
                "generation_href_relative": href_relative,
                "generation_href_absolute": urljoin(BASE_URL, href_relative),
            }
        )

    return rows


def extract_car_links_from_html(html: str, manufacturer_slug: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    found: set[str] = set()
    prefix = f"{manufacturer_slug}/"

    for a in soup.select("a.cb"):
        href = clean_text(a.get("href", ""))
        if href and href.startswith(prefix) and href.count("-") >= 4:
            found.add(urljoin(BASE_URL, href))

    return sorted(found)


# ---------------------------------------------------------------------------
# Summary / inspection
# ---------------------------------------------------------------------------

def count_generation_versions(links_csv_path: Path | None) -> dict[str, int]:
    if not links_csv_path or not links_csv_path.exists():
        return {}
    counts: dict[str, int] = {}
    for row in read_csv_rows(links_csv_path):
        name = first_non_empty(row, ["generation_name", "generation_name_canonical", "generation_id"])
        if not name:
            name = "SIN_GENERACION"
        counts[name] = counts.get(name, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[0]))


def inspect_db_summary(db_path: Path) -> dict[str, Any]:
    if not db_path.exists():
        return {"available": False}

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
    except Exception:
        return {"available": False}

    try:
        table_names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "T_Versiones" not in table_names:
            return {"available": False}

        cols = [row[1] for row in conn.execute("PRAGMA table_info('T_Versiones')")]
        result: dict[str, Any] = {"available": True, "columns": cols, "by_model": [], "by_generation": []}

        manufacturer_col = next((c for c in ["manufacturer_name", "manufacturer", "marca"] if c in cols), None)
        model_col = next((c for c in ["model_name", "model", "modelo"] if c in cols), None)
        generation_col = next((c for c in ["generation_name", "generation", "generacion"] if c in cols), None)
        version_col = next((c for c in ["version_name", "version"] if c in cols), None)

        if manufacturer_col and model_col:
            q = f"""
            SELECT {manufacturer_col} AS manufacturer_name, {model_col} AS model_name, COUNT(*) AS total
            FROM T_Versiones
            GROUP BY {manufacturer_col}, {model_col}
            ORDER BY {manufacturer_col}, {model_col}
            """
            result["by_model"] = [dict(row) for row in conn.execute(q)]

        if manufacturer_col and model_col and generation_col:
            distinct_expr = f", COUNT(DISTINCT {version_col}) AS distinct_version_names" if version_col else ""
            q = f"""
            SELECT {manufacturer_col} AS manufacturer_name,
                   {model_col} AS model_name,
                   {generation_col} AS generation_name,
                   COUNT(*) AS total_versions
                   {distinct_expr}
            FROM T_Versiones
            GROUP BY {manufacturer_col}, {model_col}, {generation_col}
            ORDER BY {manufacturer_col}, {model_col}, {generation_col}
            """
            result["by_generation"] = [dict(row) for row in conn.execute(q)]

        return result
    finally:
        conn.close()


def merge_registry_with_db_models(registry: list[dict[str, Any]], db_summary: dict[str, Any]) -> list[dict[str, Any]]:
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for row in registry:
        key = (clean_text(row.get("manufacturer_name")).lower(), clean_text(row.get("model_name")).lower())
        merged[key] = dict(row)

    if db_summary.get("available"):
        for row in db_summary.get("by_model", []):
            manufacturer = clean_text(row.get("manufacturer_name"))
            model = clean_text(row.get("model_name"))
            key = (manufacturer.lower(), model.lower())
            if key not in merged:
                merged[key] = {
                    "manufacturer_name": manufacturer,
                    "model_name": model,
                    "manufacturer_slug": slugify(manufacturer),
                    "model_slug": slugify(model),
                    "status": "db_only",
                }

    return sorted(merged.values(), key=lambda r: (r.get("manufacturer_slug", ""), r.get("model_slug", "")))

def print_models_summary() -> None:
    phase("RESUMEN DE MODELOS")
    registry = load_registry()
    db_summary = inspect_db_summary(DEFAULT_DB)
    registry = merge_registry_with_db_models(registry, db_summary)
    if not registry:
        warn("No hay modelos registrados ni modelos detectados en DB.")
        return

    by_model_db: dict[tuple[str, str], Any] = {}
    by_generation_db: dict[tuple[str, str], list[dict[str, Any]]] = {}
    if db_summary.get("available"):
        for row in db_summary.get("by_model", []):
            key = (clean_text(row.get("manufacturer_name")).lower(), clean_text(row.get("model_name")).lower())
            by_model_db[key] = row
        for row in db_summary.get("by_generation", []):
            key = (clean_text(row.get("manufacturer_name")).lower(), clean_text(row.get("model_name")).lower())
            by_generation_db.setdefault(key, []).append(row)

    for idx, row in enumerate(sorted(registry, key=lambda r: (r.get("manufacturer_slug", ""), r.get("model_slug", ""))), start=1):
        manufacturer = row["manufacturer_name"]
        model = row["model_name"]
        key = (manufacturer.lower(), model.lower())
        links_path = path_from_registry(row.get("links_csv_path"))
        generations_path = path_from_registry(row.get("generations_csv_path"))
        generation_rows = read_csv_rows(generations_path) if generations_path and generations_path.exists() else []
        generation_counts = count_generation_versions(links_path)
        total_links = sum(generation_counts.values())

        print(f"\n{idx}. {manufacturer} {model}")
        print(f"   status: {row.get('status', 'sin_estado')}")
        print(f"   generaciones registradas: {len(generation_rows)}")
        print(f"   links/versiones fuente: {total_links}")

        db_row = by_model_db.get(key)
        if db_row:
            print(f"   versiones en DB: {db_row.get('total')}")
        else:
            print("   versiones en DB: n/d")

        if generation_counts:
            print("   versiones por generación (fuente):")
            for gen_name, total in generation_counts.items():
                print(f"     - {gen_name}: {total}")

        db_generations = by_generation_db.get(key, [])
        if db_generations:
            print("   versiones por generación (DB):")
            for item in db_generations:
                gen_name = item.get("generation_name") or "SIN_GENERACION"
                total = item.get("total_versions")
                print(f"     - {gen_name}: {total}")


# ---------------------------------------------------------------------------
# Acquisition unified flow
# ---------------------------------------------------------------------------

def register_model_entry(
    manufacturer_name: str,
    manufacturer_href_relative: str,
    model_name: str,
    model_href_absolute: str = "",
    model_href_relative: str = "",
    generations_csv_path: Path | None = None,
    links_csv_path: Path | None = None,
) -> dict[str, Any]:
    manufacturer_name = clean_text(manufacturer_name)
    model_name = clean_text(model_name)
    manufacturer_slug = slugify(manufacturer_name)
    model_slug = slugify(model_name)
    truth_dir = model_truth_dir(manufacturer_name, model_name)
    truth_dir.mkdir(parents=True, exist_ok=True)

    current = get_registry_entry(manufacturer_slug, model_slug) or {}
    entry = {
        "manufacturer_name": manufacturer_name,
        "manufacturer_slug": manufacturer_slug,
        "manufacturer_href_relative": clean_text(manufacturer_href_relative).strip("/") + "/",
        "manufacturer_id": generate_id(manufacturer_name, clean_text(manufacturer_href_relative).strip("/") + "/"),
        "model_name": model_name,
        "model_slug": model_slug,
        "model_id": generate_id(manufacturer_name, model_name),
        "model_href_relative": model_href_relative or current.get("model_href_relative", ""),
        "model_href_absolute": model_href_absolute or current.get("model_href_absolute", ""),
        "truth_dir": relative_to_repo(truth_dir),
        "generations_csv_path": relative_to_repo(generations_csv_path) if generations_csv_path else current.get("generations_csv_path"),
        "links_csv_path": relative_to_repo(links_csv_path) if links_csv_path else current.get("links_csv_path"),
        "status": current.get("status", "registered"),
        "created_at": current.get("created_at", now_utc_iso()),
        "updated_at": now_utc_iso(),
    }
    return upsert_registry_entry(entry)


def import_models_from_html() -> None:
    phase("ADQUISICION · IMPORTAR MODELOS DESDE HTML")
    manufacturer = prompt("Marca", "SEAT")
    manufacturer_href_relative = prompt("Slug relativo fabricante", slugify(manufacturer))
    html_path = Path(prompt("Ruta HTML listado modelos"))
    ensure_file(html_path, "HTML de modelos")

    html = html_path.read_text(encoding="utf-8")
    rows = parse_models_html(html, manufacturer, manufacturer_href_relative)
    if not rows:
        raise OrbisError("No se detectaron modelos en el HTML.")

    manufacturer_slug = slugify(manufacturer)
    output_csv = TRUTH_BASE / f"{manufacturer_slug}_modelos.csv"
    write_csv_rows(
        output_csv,
        rows,
        [
            "manufacturer_id",
            "manufacturer_name",
            "manufacturer_name_upper",
            "model_id",
            "model_name",
            "model_name_upper",
            "model_href_relative",
            "model_href_absolute",
        ],
    )

    for row in rows:
        register_model_entry(
            manufacturer_name=row["manufacturer_name"],
            manufacturer_href_relative=manufacturer_href_relative,
            model_name=row["model_name"],
            model_href_absolute=row["model_href_absolute"],
            model_href_relative=row["model_href_relative"],
        )

    info(f"Modelos detectados: {len(rows)}")
    info(f"CSV generado: {output_csv}")


def generate_generations_csv_for_model() -> None:
    phase("ADQUISICION · GENERAR CSV DE GENERACIONES")
    entry = select_registered_model()
    default_html = model_truth_dir(entry["manufacturer_name"], entry["model_name"]) / "model_page_source.html"
    html_path = Path(prompt("Ruta HTML página del modelo", str(default_html)))
    ensure_file(html_path, "HTML del modelo")

    html = html_path.read_text(encoding="utf-8")
    rows = parse_generations_html(
        html=html,
        manufacturer_name=entry["manufacturer_name"],
        manufacturer_href_relative=entry["manufacturer_href_relative"],
        model_name=entry["model_name"],
    )
    if not rows:
        raise OrbisError("No se detectaron generaciones en el HTML.")

    output_csv = model_truth_dir(entry["manufacturer_name"], entry["model_name"]) / "generaciones.csv"
    write_csv_rows(
        output_csv,
        rows,
        [
            "manufacturer_id",
            "manufacturer_name",
            "manufacturer_name_upper",
            "model_id",
            "model_name",
            "model_name_upper",
            "generation_id",
            "generation_name",
            "generation_name_canonical",
            "generation_name_upper",
            "year_start",
            "year_end",
            "year_end_raw",
            "generation_href_relative",
            "generation_href_absolute",
        ],
    )

    updated = register_model_entry(
        manufacturer_name=entry["manufacturer_name"],
        manufacturer_href_relative=entry["manufacturer_href_relative"],
        model_name=entry["model_name"],
        model_href_absolute=entry.get("model_href_absolute", ""),
        model_href_relative=entry.get("model_href_relative", ""),
        generations_csv_path=output_csv,
    )
    updated["status"] = "generations_ready"
    upsert_registry_entry(updated)

    info(f"Generaciones detectadas: {len(rows)}")
    info(f"CSV generado: {output_csv}")


def save_links_output(rows: list[dict[str, str]], output_file: Path) -> None:
    deduped: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        generation_id = clean_text(row.get("generation_id"))
        car_url = clean_text(row.get("car_url"))
        if not generation_id or not car_url:
            continue
        deduped[(generation_id, car_url)] = {
            "generation_id": generation_id,
            "generation_name": clean_text(row.get("generation_name")),
            "generation_url": clean_text(row.get("generation_url")),
            "car_url": car_url,
        }
    ordered = sorted(deduped.values(), key=lambda x: (x["generation_name"], x["car_url"]))
    write_csv_rows(output_file, ordered, ["generation_id", "generation_name", "generation_url", "car_url"])


def capture_links_for_model() -> None:
    phase("ADQUISICION · CAPTURA SEMIMANUAL DE LINKS")
    entry = select_registered_model(require_generations=True)
    generations_csv = path_from_registry(entry.get("generations_csv_path"))
    if not generations_csv:
        raise OrbisError("Falta CSV de generaciones.")

    generations = read_csv_rows(generations_csv)
    if not generations:
        raise OrbisError("CSV de generaciones vacío.")

    truth_dir = model_truth_dir(entry["manufacturer_name"], entry["model_name"])
    checkpoint_file = truth_dir / "capture_checkpoint.json"
    output_file = truth_dir / "car_links_output.csv"

    existing_rows: list[dict[str, str]] = read_csv_rows(output_file) if output_file.exists() else []
    seen_pairs = {(clean_text(r.get("generation_id")), clean_text(r.get("car_url"))) for r in existing_rows}
    all_rows = [
        {
            "generation_id": clean_text(r.get("generation_id")),
            "generation_name": clean_text(r.get("generation_name")),
            "generation_url": clean_text(r.get("generation_url")),
            "car_url": clean_text(r.get("car_url")),
        }
        for r in existing_rows
        if clean_text(r.get("car_url"))
    ]

    start_index = 0
    if checkpoint_file.exists():
        try:
            start_index = json.loads(checkpoint_file.read_text(encoding="utf-8")).get("last_completed_index", -1) + 1
        except Exception:
            start_index = 0

    if sb_cdp is None:
        raise OrbisError("No está disponible seleniumbase/sb_cdp para captura semimanual.")

    manufacturer_slug = entry["manufacturer_slug"]

    print(f"Total generaciones a procesar: {len(generations)}")
    print(f"Reanudando desde índice: {start_index}")

    for idx, generation in enumerate(generations):
        if idx < start_index:
            continue

        generation_id = first_non_empty(generation, ["generation_id"])
        generation_name = first_non_empty(generation, ["generation_name_canonical", "generation_name"])
        generation_url = first_non_empty(generation, ["generation_href_absolute", "generation_url", "url", "href"])
        if not generation_url:
            warn(f"Generación sin URL, se omite: {generation_name or generation_id}")
            checkpoint_file.write_text(json.dumps({"last_completed_index": idx}, ensure_ascii=False, indent=2), encoding="utf-8")
            continue

        print("=" * 80)
        print(f"[{idx + 1}/{len(generations)}] Abriendo: {generation_url}")
        print(f"generation_id: {generation_id}")
        print(f"generation_name: {generation_name}")

        browser = sb_cdp.Chrome(uc=True, url=generation_url)
        browser.sleep(2)

        print(
            "Modo semiautomático activo.\n"
            "Haz scroll manualmente y usa:\n"
            "  ENTER = capturar links visibles ahora\n"
            "  c     = capturar y completar esta generación\n"
            "  s     = saltar esta generación\n"
            "  q     = guardar y salir\n"
        )

        while True:
            command = input("Comando: ").strip().lower()

            if command == "q":
                try:
                    browser.quit()
                except Exception:
                    pass
                save_links_output(all_rows, output_file)
                checkpoint_file.write_text(json.dumps({"last_completed_index": idx - 1}, ensure_ascii=False, indent=2), encoding="utf-8")
                updated = register_model_entry(
                    manufacturer_name=entry["manufacturer_name"],
                    manufacturer_href_relative=entry["manufacturer_href_relative"],
                    model_name=entry["model_name"],
                    model_href_absolute=entry.get("model_href_absolute", ""),
                    model_href_relative=entry.get("model_href_relative", ""),
                    generations_csv_path=generations_csv,
                    links_csv_path=output_file,
                )
                updated["status"] = "links_partial"
                upsert_registry_entry(updated)
                print("Proceso detenido por el usuario. Estado guardado.")
                return

            if command == "s":
                try:
                    browser.quit()
                except Exception:
                    pass
                checkpoint_file.write_text(json.dumps({"last_completed_index": idx}, ensure_ascii=False, indent=2), encoding="utf-8")
                print("Generación saltada.")
                break

            if command in {"", "c"}:
                html = browser.get_page_source()
                page_links = extract_car_links_from_html(html, manufacturer_slug=manufacturer_slug)
                added_now = 0
                for car_url in page_links:
                    pair = (generation_id, car_url)
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)
                    all_rows.append(
                        {
                            "generation_id": generation_id,
                            "generation_name": generation_name,
                            "generation_url": generation_url,
                            "car_url": car_url,
                        }
                    )
                    added_now += 1

                total_generation = len([r for r in all_rows if r["generation_id"] == generation_id])
                save_links_output(all_rows, output_file)
                print(
                    f"Captura realizada. Nuevos links añadidos: {added_now} | "
                    f"Total acumulado para esta generación: {total_generation}"
                )

                if command == "c":
                    checkpoint_file.write_text(json.dumps({"last_completed_index": idx}, ensure_ascii=False, indent=2), encoding="utf-8")
                    try:
                        browser.quit()
                    except Exception:
                        pass
                    print(f"Generación completada. Total final para {generation_name}: {total_generation}")
                    break
                continue

            print("Comando no válido. Usa ENTER, c, s o q.")

    updated = register_model_entry(
        manufacturer_name=entry["manufacturer_name"],
        manufacturer_href_relative=entry["manufacturer_href_relative"],
        model_name=entry["model_name"],
        model_href_absolute=entry.get("model_href_absolute", ""),
        model_href_relative=entry.get("model_href_relative", ""),
        generations_csv_path=generations_csv,
        links_csv_path=output_file,
    )
    updated["status"] = "links_ready"
    upsert_registry_entry(updated)
    print(f"Proceso completado. Total pares únicos generación+coche: {len(all_rows)}")
    print(f"CSV generado: {output_file}")


# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------

def run_command(name: str, args: list[str], interactive: bool = False) -> StepResult:
    env = os.environ.copy()
    env.update({"PYTHONPATH": ".", "PYTHONIOENCODING": "utf-8"})
    proc = subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        env=env,
        capture_output=not interactive,
    )
    return StepResult(
        name=name,
        ok=(proc.returncode == 0),
        returncode=proc.returncode,
        stdout="" if interactive else proc.stdout,
        stderr="" if interactive else proc.stderr,
        command=args,
    )


def print_step_result(result: StepResult, stop_on_error: bool = True) -> None:
    status = "OK" if result.ok else "ERROR"
    print(f"[{result.name}] {status} (code={result.returncode})")
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    if stop_on_error and not result.ok:
        raise OrbisError(f"Fallo en fase {result.name}")


def run_iig(input_json: Path) -> StepResult:
    ensure_file(VALIDATION_RUNNER, "runner IIG")
    ensure_file(input_json, "JSON de entrada IIG")
    ensure_file(DEFAULT_CONTRACT, "contrato")
    return run_command("IIG", [sys.executable, str(VALIDATION_RUNNER), "--input", str(input_json), "--contract", str(DEFAULT_CONTRACT)])


def run_dvl_classification(input_json: Path, output_prefix: str) -> tuple[StepResult, Path, Path, Path]:
    ensure_file(CLASSIFY_DVL_RUNNER, "runner DVL")
    ensure_file(input_json, "JSON de entrada DVL")
    valid_output = DEFAULT_OUTPUT_BASE / f"{output_prefix}_ingestables.json"
    pending_output = PENDING_DIR / "pendientes_dvl.json"
    rejected_output = PENDING_DIR / "rechazados_tecnicos.json"
    result = run_command(
        "DVL",
        [
            sys.executable,
            str(CLASSIFY_DVL_RUNNER),
            "--input",
            str(input_json),
            "--valid-output",
            str(valid_output),
            "--pending-output",
            str(pending_output),
            "--rejected-output",
            str(rejected_output),
        ],
    )
    return result, valid_output, pending_output, rejected_output


def run_lote_validation(input_json: Path) -> StepResult:
    ensure_file(LOTE_RUNNER, "runner validación de lote")
    ensure_file(input_json, "JSON de entrada lote")
    return run_command("LOTE", [sys.executable, str(LOTE_RUNNER), "--input", str(input_json)])


def mark_batch_passed(input_json: Path, output_json: Path) -> StepResult:
    ensure_file(BATCH_MARK_RUNNER, "runner batch")
    return run_command("BATCH_STATUS", [sys.executable, str(BATCH_MARK_RUNNER), "--input", str(input_json), "--output", str(output_json)])


def run_id_resolution(input_json: Path, output_json: Path, db_path: Path) -> StepResult:
    ensure_file(ID_RESOLUTION_RUNNER, "runner ID resolution")
    ensure_file(db_path, "base de datos")
    return run_command(
        "ID_RESOLUTION",
        [sys.executable, str(ID_RESOLUTION_RUNNER), "--db-path", str(db_path), "--input", str(input_json), "--output", str(output_json)],
    )


def run_ingestion(dataset_json: Path, db_path: Path) -> StepResult:
    ensure_file(INGESTION_RUNNER, "runner ingestión")
    ensure_file(db_path, "base de datos")
    return run_command(
        "INGESTION",
        [sys.executable, str(INGESTION_RUNNER), "--db-path", str(db_path), "--dataset", str(dataset_json)],
    )


def run_scraper(csv_path: Path, output_dir: Path, start_page: str, limit: str) -> StepResult:
    ensure_file(SCRAPER_RUNNER, "runner scraper")
    ensure_file(csv_path, "CSV de scraping")
    ensure_file(DEFAULT_CONTRACT, "contrato")
    return run_command(
        "SCRAPER",
        [
            sys.executable,
            str(SCRAPER_RUNNER),
            "--csv",
            str(csv_path),
            "--start-page",
            str(start_page),
            "--limit",
            str(limit),
            "--contract",
            str(DEFAULT_CONTRACT),
            "--output-dir",
            str(output_dir),
        ],
        interactive=True,
    )


def execute_full_catalog_pipeline_for_model() -> None:
    phase("CATALOGO · PIPELINE COMPLETO POR MODELO")
    entry = select_registered_model(require_links=True)
    csv_path = path_from_registry(entry.get("links_csv_path"))
    if not csv_path:
        raise OrbisError("El modelo no tiene CSV de links.")

    label = f"{entry['manufacturer_slug']}_{entry['model_slug']}_pipeline"
    db_path = Path(prompt("Ruta DB", str(DEFAULT_DB)))
    start_page = prompt("Start page", "1")
    limit = prompt("Limit", "10")
    output_dir = Path(prompt("Output dir", str(build_output_dir(label))))

    clean_json = output_dir / "clean_version_dicts.json"
    raw_json = output_dir / "raw_version_dicts.json"
    batch_ok_json = DEFAULT_OUTPUT_BASE / f"{output_dir.name}_batch_ok.json"
    resolved_json = DEFAULT_OUTPUT_BASE / f"{output_dir.name}_resuelto.json"

    results: list[StepResult] = []
    step = run_scraper(csv_path, output_dir, start_page, limit)
    results.append(step)
    if clean_json.exists() and raw_json.exists():
        info("[SCRAPER] OK - artefactos generados correctamente")
        if not step.ok:
            warn("[SCRAPER] Exit code no limpio, pero datos válidos. Se continúa.")
    else:
        raise OrbisError("Fallo en fase SCRAPER: no se generaron clean_version_dicts.json y raw_version_dicts.json")

    step = run_iig(clean_json)
    results.append(step)
    print_step_result(step)

    step, valid_output, pending_output, rejected_output = run_dvl_classification(clean_json, output_dir.name)
    results.append(step)
    print_step_result(step)

    step = run_lote_validation(valid_output)
    results.append(step)
    print_step_result(step)

    step = mark_batch_passed(valid_output, batch_ok_json)
    results.append(step)
    print_step_result(step)

    step = run_id_resolution(batch_ok_json, resolved_json, db_path)
    results.append(step)
    print_step_result(step)

    step = run_ingestion(resolved_json, db_path)
    results.append(step)
    print_step_result(step)

    phase("RESUMEN FINAL")
    for item in results:
        print(f"[{item.name}] {'OK' if item.ok else 'ERROR'}")
    print(f"[PENDIENTES] {pending_output}")
    print(f"[RECHAZADOS] {rejected_output}")
    print(f"[INGESTABLES] {valid_output}")
    print(f"[BATCH_OK] {batch_ok_json}")
    print(f"[RESUELTO] {resolved_json}")


# ---------------------------------------------------------------------------
# Bootstrapping / manual shortcuts
# ---------------------------------------------------------------------------

def bootstrap_seat_leon() -> None:
    phase("BOOTSTRAP · SEAT LEON")
    entry = register_model_entry(
        manufacturer_name="SEAT",
        manufacturer_href_relative="seat/",
        model_name="León",
        model_href_relative="seat/Leon",
        model_href_absolute=urljoin(BASE_URL, "seat/Leon"),
    )
    entry["status"] = "registered"
    upsert_registry_entry(entry)
    info("Modelo SEAT León registrado en model_registry.json")
    info("Siguiente paso: generar su HTML de modelo y ejecutar 'Generar CSV de generaciones'.")




def capture_model_html() -> None:
    phase("ADQUISICION · CAPTURAR HTML DE MODELO")
    entry = select_registered_model()
    default_url = entry.get("model_href_absolute") or urljoin(BASE_URL, entry.get("model_href_relative", ""))
    output_path = model_truth_dir(entry["manufacturer_name"], entry["model_name"]) / "model_page_source.html"
    get_page_source_to_file(default_url=default_url, output_path=output_path)


def capture_generic_html() -> None:
    phase("ADQUISICION · GET PAGE SOURCE")
    get_page_source_to_file()

# ---------------------------------------------------------------------------
# Menus
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Concesionarios
# ---------------------------------------------------------------------------

def run_concesionarios_pipeline(input_json: Path, report_json: Path, db_path: Path) -> StepResult:
    ensure_file(CONCESIONARIOS_PIPELINE_RUNNER, "runner pipeline T_Concesionarios")
    ensure_file(input_json, "JSON entrada concesionarios")
    ensure_file(db_path, "base de datos")
    return run_command(
        "CONCESIONARIOS_PIPELINE",
        [
            sys.executable,
            str(CONCESIONARIOS_PIPELINE_RUNNER),
            "--input",
            str(input_json),
            "--db-path",
            str(db_path),
            "--report",
            str(report_json),
        ],
    )


def run_concesionarios_db_ingestion(input_json: Path, db_path: Path) -> StepResult:
    ensure_file(CONCESIONARIOS_DB_INGESTION_RUNNER, "runner DB ingestion T_Concesionarios")
    ensure_file(input_json, "JSON entrada concesionarios")
    ensure_file(db_path, "base de datos")
    return run_command(
        "CONCESIONARIOS_DB_INGESTION",
        [
            sys.executable,
            str(CONCESIONARIOS_DB_INGESTION_RUNNER),
            "--input",
            str(input_json),
            "--db-path",
            str(db_path),
        ],
    )


def run_concesionarios_pending_audit(report_json: Path, output_json: Path) -> StepResult:
    ensure_file(CONCESIONARIOS_AUDIT_PENDING_RUNNER, "runner auditoría pendientes T_Concesionarios")
    ensure_file(report_json, "reporte pipeline concesionarios")
    return run_command(
        "CONCESIONARIOS_PENDING_AUDIT",
        [
            sys.executable,
            str(CONCESIONARIOS_AUDIT_PENDING_RUNNER),
            "--report",
            str(report_json),
            "--output",
            str(output_json),
        ],
    )


def run_concesionarios_build_merged(inputs: list[Path], output_json: Path) -> StepResult:
    ensure_file(CONCESIONARIOS_BUILD_MERGED_RUNNER, "runner build merged concesionarios")
    for path in inputs:
        ensure_file(path, "input fuente concesionarios")

    return run_command(
        "CONCESIONARIOS_BUILD_MERGED",
        [
            sys.executable,
            str(CONCESIONARIOS_BUILD_MERGED_RUNNER),
            "--inputs",
            *[str(p) for p in inputs],
            "--output",
            str(output_json),
        ],
    )


def execute_concesionarios_pipeline_single_source(source_name: str, input_json: Path) -> None:
    phase(f"CONCESIONARIOS · PIPELINE FUENTE {source_name.upper()}")

    db_path = Path(prompt("Ruta DB", str(DEFAULT_DB)))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_json = DEFAULT_OUTPUT_BASE / f"concesionarios_{source_name}_pipeline_{stamp}.json"
    audit_json = DEFAULT_OUTPUT_BASE / f"concesionarios_{source_name}_pending_audit_{stamp}.json"

    results: list[StepResult] = []

    step = run_concesionarios_pipeline(input_json, report_json, db_path)
    results.append(step)
    print_step_result(step)

    step = run_concesionarios_db_ingestion(input_json, db_path)
    results.append(step)
    print_step_result(step)

    step = run_concesionarios_pending_audit(report_json, audit_json)
    results.append(step)
    print_step_result(step, stop_on_error=False)

    phase("RESUMEN CONCESIONARIOS")
    for item in results:
        print(f"[{item.name}] {'OK' if item.ok else 'ERROR'}")
    print(f"[INPUT] {input_json}")
    print(f"[REPORTE] {report_json}")
    print(f"[AUDIT_PENDIENTES] {audit_json}")


def execute_concesionarios_pipeline_multifuente() -> None:
    phase("CONCESIONARIOS · PIPELINE MULTIFUENTE")

    db_path = Path(prompt("Ruta DB", str(DEFAULT_DB)))

    autocasion_input = Path(
        prompt(
            "Input Autocasión",
            str(CONCESIONARIOS_BASE / "autocasion" / "raw_exploratorio_autocasion.json"),
        )
    )

    cochesnet_input = Path(
        prompt(
            "Input Coches.net",
            str(CONCESIONARIOS_BASE / "cochesnet" / "raw_exploratorio_cochesnet.json"),
        )
    )

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_json = CONCESIONARIOS_SAMPLE_BASE / f"concesionarios_merged_multifuente_{stamp}.json"
    report_json = DEFAULT_OUTPUT_BASE / f"concesionarios_merged_pipeline_{stamp}.json"
    audit_json = DEFAULT_OUTPUT_BASE / f"concesionarios_merged_pending_audit_{stamp}.json"

    results: list[StepResult] = []

    step = run_concesionarios_build_merged(
        inputs=[autocasion_input, cochesnet_input],
        output_json=merged_json,
    )
    results.append(step)
    print_step_result(step)

    step = run_concesionarios_pipeline(merged_json, report_json, db_path)
    results.append(step)
    print_step_result(step)

    step = run_concesionarios_db_ingestion(merged_json, db_path)
    results.append(step)
    print_step_result(step)

    step = run_concesionarios_pending_audit(report_json, audit_json)
    results.append(step)
    print_step_result(step, stop_on_error=False)

    phase("RESUMEN CONCESIONARIOS MULTIFUENTE")
    for item in results:
        print(f"[{item.name}] {'OK' if item.ok else 'ERROR'}")
    print(f"[MERGED_INPUT] {merged_json}")
    print(f"[REPORTE] {report_json}")
    print(f"[AUDIT_PENDIENTES] {audit_json}")


def menu_concesionarios() -> None:
    while True:
        phase("CONCESIONARIOS")
        print("1. Ejecutar pipeline Autocasión")
        print("2. Ejecutar pipeline Coches.net")
        print("3. Ejecutar pipeline multifuente")
        print("4. Volver")
        choice = input("> ").strip()

        try:
            if choice == "1":
                execute_concesionarios_pipeline_single_source(
                    source_name="autocasion",
                    input_json=CONCESIONARIOS_BASE / "autocasion" / "raw_exploratorio_autocasion.json",
                )
            elif choice == "2":
                execute_concesionarios_pipeline_single_source(
                    source_name="cochesnet",
                    input_json=CONCESIONARIOS_BASE / "cochesnet" / "raw_exploratorio_cochesnet.json",
                )
            elif choice == "3":
                execute_concesionarios_pipeline_multifuente()
            elif choice == "4":
                return
            else:
                warn("Opción no válida.")
        except OrbisError as exc:
            error(str(exc))
        except KeyboardInterrupt:
            warn("Operación cancelada por usuario.")
        except Exception as exc:
            error(f"Fallo inesperado: {exc}")
def menu_acquisition() -> None:
    while True:
        phase("ADQUISICION CATALOGO")
        print("1. Importar modelos desde HTML")
        print("2. Capturar HTML de un modelo (get_page_source)")
        print("3. Generar CSV de generaciones para un modelo")
        print("4. Capturar links/versiones por generaciones")
        print("5. Bootstrap SEAT León")
        print("6. Get page source genérico")
        print("7. Volver")
        choice = input("> ").strip()
        try:
            if choice == "1":
                import_models_from_html()
            elif choice == "2":
                capture_model_html()
            elif choice == "3":
                generate_generations_csv_for_model()
            elif choice == "4":
                capture_links_for_model()
            elif choice == "5":
                bootstrap_seat_leon()
            elif choice == "6":
                capture_generic_html()
            elif choice == "7":
                return
            else:
                warn("Opción no válida.")
        except OrbisError as exc:
            error(str(exc))
        except KeyboardInterrupt:
            warn("Operación cancelada por usuario.")
        except Exception as exc:
            error(f"Fallo inesperado: {exc}")


def menu_models() -> None:
    while True:
        phase("GESTION DE MODELOS")
        print("1. Ver resumen de modelos")
        print("2. Registrar modelo manualmente")
        print("3. Volver")
        choice = input("> ").strip()
        try:
            if choice == "1":
                print_models_summary()
            elif choice == "2":
                manufacturer = prompt("Marca", "SEAT")
                model = prompt("Modelo")
                manufacturer_href_relative = prompt("Slug relativo fabricante", slugify(manufacturer))
                model_href_relative = prompt("Slug relativo modelo", f"{slugify(manufacturer)}/{slugify(model)}")
                entry = register_model_entry(
                    manufacturer_name=manufacturer,
                    manufacturer_href_relative=manufacturer_href_relative,
                    model_name=model,
                    model_href_relative=model_href_relative,
                    model_href_absolute=urljoin(BASE_URL, model_href_relative),
                )
                entry["status"] = "registered"
                upsert_registry_entry(entry)
                info(f"Modelo registrado: {manufacturer} {model}")
            elif choice == "3":
                return
            else:
                warn("Opción no válida.")
        except OrbisError as exc:
            error(str(exc))
        except KeyboardInterrupt:
            warn("Operación cancelada por usuario.")
        except Exception as exc:
            error(f"Fallo inesperado: {exc}")


def menu_catalog() -> None:
    while True:
        phase("CATALOGO")
        print("1. Ejecutar pipeline completo por modelo (scraping -> DB)")
        print("2. Volver")
        choice = input("> ").strip()
        try:
            if choice == "1":
                execute_full_catalog_pipeline_for_model()
            elif choice == "2":
                return
            else:
                warn("Opción no válida.")
        except OrbisError as exc:
            error(str(exc))
        except KeyboardInterrupt:
            warn("Operación cancelada por usuario.")
        except Exception as exc:
            error(f"Fallo inesperado: {exc}")


def main() -> None:
    while True:
        phase("ORBIS DRIVE · ORQUESTADOR UNIFICADO")
        print("1. Catálogo")
        print("2. Adquisición catálogo")
        print("3. Gestión y resumen de modelos")
        print("4. Concesionarios")
        print("5. Salir")
        choice = input("> ").strip()
        if choice == "1":
            menu_catalog()
        elif choice == "2":
            menu_acquisition()
        elif choice == "3":
            menu_models()
        elif choice == "4":
            menu_concesionarios()
        elif choice == "5":
            print("Saliendo de Orbis Drive.")
            return
        else:
            warn("Opción no válida.")


if __name__ == "__main__":
    main()
