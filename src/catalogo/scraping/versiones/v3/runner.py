from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .browser_adapters import build_browser
from .checkpoints import (
    append_error,
    append_json_array,
    load_checkpoint_state,
    mark_completed,
    mark_failed,
)
from .field_mapping import map_raw_to_clean
from .parser import parse_version_html

SCRAPER_VERSION = "v3"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_output_structure(output_dir: Path) -> dict[str, Path]:
    checkpoints_dir = output_dir / "checkpoints"
    errors_dir = output_dir / "errors"

    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    errors_dir.mkdir(parents=True, exist_ok=True)

    return {
        "output_dir": output_dir,
        "checkpoints_dir": checkpoints_dir,
        "errors_dir": errors_dir,
        "raw_json": output_dir / "raw_version_dicts.json",
        "clean_json": output_dir / "clean_version_dicts.json",
    }


def _read_contract(contract_path: str | Path) -> dict[str, Any]:
    contract_file = Path(contract_path)
    with contract_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_urls_from_csv(csv_path: str | Path) -> list[str]:
    csv_file = Path(csv_path)
    urls: list[str] = []

    with csv_file.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        lowered = {name.lower().strip(): name for name in fieldnames}
        candidate_columns = [
            "car_url",
            "url",
            "link",
            "href",
            "source_url",
            "source_version_url",
            "version_url",
        ]

        selected_column = None
        for candidate in candidate_columns:
            if candidate in lowered:
                selected_column = lowered[candidate]
                break

        if selected_column is not None:
            for row in reader:
                value = (row.get(selected_column) or "").strip()
                if value:
                    urls.append(value)
            return urls

    # Fallback defensivo
    with csv_file.open("r", encoding="utf-8-sig", newline="") as f:
        raw_reader = csv.reader(f)
        next(raw_reader, None)

        for row in raw_reader:
            if not row:
                continue
            value = (row[0] or "").strip()
            if value:
                urls.append(value)

    return urls


def _build_metadata(
    source_url: str,
    capture_mode: str,
    parser_version: str,
    quality_flags: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "scraper_version": SCRAPER_VERSION,
        "parser_version": parser_version,
        "capture_mode": capture_mode,
        "source": "encycarpedia",
        "source_url": source_url,
        "quality_flags": quality_flags or [],
        "scrape_timestamp": _utc_now_iso(),
    }


def _build_output_record(
    raw_dict: dict[str, Any],
    clean_dict: dict[str, Any],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "raw": raw_dict,
        "clean": clean_dict,
        "metadata": metadata,
    }


def _validate_required_minimum_fields(
    clean_dict: dict[str, Any],
    contract: dict[str, Any],
) -> list[str]:
    missing: list[str] = []
    required_fields = contract.get("required_minimum_fields", [])

    for field_name in required_fields:
        value = clean_dict.get(field_name)
        if value is None:
            missing.append(field_name)
            continue
        if isinstance(value, str) and not value.strip():
            missing.append(field_name)

    return missing


def _process_local_html_file(
    html_path: str | Path,
    contract: dict[str, Any],
    paths: dict[str, Path],
) -> None:
    html_file = Path(html_path)
    html_text = html_file.read_text(encoding="utf-8", errors="ignore")

    raw_dict, parser_version = parse_version_html(
        html=html_text,
        source_url=str(html_file),
        contract=contract,
    )
    clean_dict = map_raw_to_clean(raw_dict=raw_dict, contract=contract)

    quality_flags: list[str] = []
    missing_required = _validate_required_minimum_fields(clean_dict, contract)
    if missing_required:
        quality_flags.append(f"missing_required:{','.join(missing_required)}")

    metadata = _build_metadata(
        source_url=str(html_file),
        capture_mode="local_html",
        parser_version=parser_version,
        quality_flags=quality_flags,
    )

    record = _build_output_record(
        raw_dict=raw_dict,
        clean_dict=clean_dict,
        metadata=metadata,
    )

    append_json_array(paths["raw_json"], record["raw"])
    append_json_array(paths["clean_json"], record["clean"])

    checkpoint_payload = {
        "status": "completed",
        "mode": "local_html",
        "source": str(html_file),
        "timestamp": _utc_now_iso(),
        "quality_flags": quality_flags,
    }
    mark_completed(paths["checkpoints_dir"], str(html_file), checkpoint_payload)

    print(f"Parseado local: {html_file}")


def _process_csv_urls(
    urls: list[str],
    contract: dict[str, Any],
    paths: dict[str, Path],
    start_page: int,
) -> None:
    state = load_checkpoint_state(paths["checkpoints_dir"])
    completed_sources = set(state.get("completed_sources", []))

    browser = build_browser()
    try:
        pending_urls = [url for url in urls if url not in completed_sources]
        print(f"[INFO] Start page: {start_page}")
        print(f"[INFO] Procesando {len(pending_urls)} URLs")

        for url in pending_urls:
            try:
                print(f"[OPEN] {url}")
                browser.open(url)
                input("[WAIT] Página cargada. Pulsa ENTER para capturar HTML... ")

                html_text = browser.get_page_source()

                raw_dict, parser_version = parse_version_html(
                    html=html_text,
                    source_url=url,
                    contract=contract,
                )
                clean_dict = map_raw_to_clean(raw_dict=raw_dict, contract=contract)

                quality_flags: list[str] = []
                missing_required = _validate_required_minimum_fields(
                    clean_dict,
                    contract,
                )
                if missing_required:
                    quality_flags.append(
                        f"missing_required:{','.join(missing_required)}"
                    )

                metadata = _build_metadata(
                    source_url=url,
                    capture_mode="manual",
                    parser_version=parser_version,
                    quality_flags=quality_flags,
                )

                record = _build_output_record(
                    raw_dict=raw_dict,
                    clean_dict=clean_dict,
                    metadata=metadata,
                )

                append_json_array(paths["raw_json"], record["raw"])
                append_json_array(paths["clean_json"], record["clean"])

                checkpoint_payload = {
                    "status": "completed",
                    "mode": "csv_manual",
                    "source": url,
                    "timestamp": _utc_now_iso(),
                    "quality_flags": quality_flags,
                }
                mark_completed(paths["checkpoints_dir"], url, checkpoint_payload)
                print(f"[OK] Procesada URL: {url}")

            except Exception as exc:
                error_payload = {
                    "status": "failed",
                    "source": url,
                    "timestamp": _utc_now_iso(),
                    "error": repr(exc),
                }
                mark_failed(paths["checkpoints_dir"], url, error_payload)
                append_error(paths["errors_dir"], url, error_payload)
                print(f"[ERROR] Fallo procesando {url}: {exc}")

    finally:
        browser.close()


def run_scraper(
    csv_path: str | None = None,
    contract_path: str | None = None,
    output_dir: str | None = None,
    html_files: list[str] | None = None,
    limit: int | None = None,
    start_page: int = 1,
) -> None:
    if not contract_path:
        raise ValueError("contract_path es obligatorio")
    if not output_dir:
        raise ValueError("output_dir es obligatorio")
    if not csv_path and not html_files:
        raise ValueError("Debes indicar --csv o --from-html")

    contract = _read_contract(contract_path)
    paths = _ensure_output_structure(Path(output_dir))

    if html_files:
        for html_file in html_files:
            _process_local_html_file(
                html_path=html_file,
                contract=contract,
                paths=paths,
            )
        return

    urls = _load_urls_from_csv(csv_path)

    if start_page < 1:
        raise ValueError("--start-page debe ser un entero mayor o igual que 1")

    start_index = start_page - 1

    if start_index >= len(urls):
        raise ValueError(
            f"--start-page={start_page} está fuera de rango. "
            f"El CSV contiene {len(urls)} URLs."
        )

    urls = urls[start_index:]

    if limit is not None:
        if limit < 1:
            raise ValueError("--limit debe ser un entero mayor que 0")
        urls = urls[:limit]

    _process_csv_urls(
        urls=urls,
        contract=contract,
        paths=paths,
        start_page=start_page,
    )


def main() -> None:
    raise SystemExit(
        "Usa scripts/scraping/run_scraper_versiones.py para ejecutar el scraper."
    )