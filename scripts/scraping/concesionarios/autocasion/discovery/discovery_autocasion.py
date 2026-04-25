#!/usr/bin/env python3
"""Discovery de URLs para Autocasión Profesional usando SeleniumBase CDP.

Objetivo:
- Recorrer la paginación del directorio nacional /profesional?page=N
- Detectar URLs de fichas de concesionario
- Detectar URLs de provincias
- Detectar URLs de paginación
- Guardar resultados trazables sin inferencia

No extrae detalle semántico del concesionario. Solo discovery.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup
from seleniumbase import sb_cdp

BASE_URL = "https://www.autocasion.com"
START_URL = f"{BASE_URL}/profesional"
OUTPUT_BASE = Path("data/external/concesionarios/autocasion")
DISCOVERY_DIR = OUTPUT_BASE / "discovery"
LOGS_DIR = OUTPUT_BASE / "logs"
SNAPSHOTS_DIR = OUTPUT_BASE / "snapshots"

DETAIL_RE = re.compile(r"^/profesional/([^/?#]+)$")
PROFESIONAL_PATH = "/profesional"

# Lista explícita de slugs territoriales observables o esperables en la fuente.
PROVINCE_SLUGS = {
    "alava", "albacete", "alicante", "almeria", "asturias", "avila", "badajoz",
    "barcelona", "burgos", "caceres", "cadiz", "cantabria", "castellon", "ceuta",
    "ciudad-real", "cordoba", "cuenca", "girona", "granada", "guadalajara", "guipuzcoa",
    "huelva", "huesca", "islas-baleares", "illes-balears", "jaen", "la-coruna",
    "a-coruna", "la-rioja", "las-palmas", "leon", "lleida", "lugo", "madrid", "malaga",
    "melilla", "murcia", "navarra", "orense", "ourense", "palencia", "pontevedra",
    "salamanca", "segovia", "sevilla", "soria", "tarragona", "sta-c-de-tenerife",
    "santa-cruz-de-tenerife", "teruel", "toledo", "valencia", "valladolid", "vizcaya",
    "zamora", "zaragoza",
}

# Landings o slugs no pertenecientes a fichas de dealer.
EXCLUDED_EXACT_SLUGS = {
    "profesional",
}
EXCLUDED_PREFIXES = (
    "ofertas-renting",
)


@dataclass
class DiscoveryRecord:
    page_url: str
    page_type: str
    discovered_url: str
    discovered_type: str
    anchor_text: Optional[str]


class Logger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, message: str) -> None:
        ts = datetime.now().isoformat(timespec="seconds")
        with self.path.open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {message}\n")



def ensure_dirs() -> None:
    for d in (OUTPUT_BASE, DISCOVERY_DIR, LOGS_DIR, SNAPSHOTS_DIR):
        d.mkdir(parents=True, exist_ok=True)



def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc or urlparse(BASE_URL).netloc
    path = parsed.path.rstrip("/") or "/"
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{scheme}://{netloc}{path}{query}"



def classify_slug(slug: str) -> str:
    slug = slug.strip().lower()
    if not slug:
        return "discarded"
    if slug in EXCLUDED_EXACT_SLUGS:
        return "discarded"
    if slug in PROVINCE_SLUGS:
        return "province"
    if any(slug.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return "discarded"
    return "detail"



def classify_profesional_url(url: str) -> Optional[str]:
    parsed = urlparse(url)
    if parsed.netloc and parsed.netloc != urlparse(BASE_URL).netloc:
        return None
    path = parsed.path.rstrip("/") or "/"

    if path == PROFESIONAL_PATH and parsed.query:
        qs = parse_qs(parsed.query)
        if "page" in qs:
            return "pagination"

    if path == PROFESIONAL_PATH and not parsed.query:
        return "directory"

    match = DETAIL_RE.match(path)
    if not match or parsed.query:
        return None

    slug = match.group(1)
    return classify_slug(slug)



def extract_links(page_url: str, html: str) -> list[DiscoveryRecord]:
    soup = BeautifulSoup(html, "html.parser")
    out: list[DiscoveryRecord] = []
    page_type = classify_profesional_url(page_url) or "unknown"

    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        absolute = normalize_url(urljoin(page_url, href))
        discovered_type = classify_profesional_url(absolute)
        if not discovered_type:
            continue
        text = " ".join(a.get_text(" ", strip=True).split()) or None
        out.append(
            DiscoveryRecord(
                page_url=page_url,
                page_type=page_type,
                discovered_url=absolute,
                discovered_type=discovered_type,
                anchor_text=text,
            )
        )
    return out



def save_snapshot(url: str, html: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9]+", "_", url)[:120].strip("_")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = SNAPSHOTS_DIR / f"discovery_{ts}_{safe}.html"
    path.write_text(html, encoding="utf-8")
    return path



def unique_records(records: Iterable[DiscoveryRecord]) -> list[DiscoveryRecord]:
    seen: set[tuple[str, str, str]] = set()
    out: list[DiscoveryRecord] = []
    for r in records:
        key = (r.page_url, r.discovered_url, r.discovered_type)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out



def load_existing_detail_urls() -> set[str]:
    path = DISCOVERY_DIR / "dealer_detail_urls.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return set(data.get("urls", []))
    except Exception:
        return set()



def save_outputs(all_records: list[DiscoveryRecord], visited_pages: list[str]) -> None:
    ts = datetime.now().strftime("%Y-%m-%d")
    detail_urls = sorted({r.discovered_url for r in all_records if r.discovered_type == "detail"})
    province_urls = sorted({r.discovered_url for r in all_records if r.discovered_type == "province"})
    pagination_urls = sorted({r.discovered_url for r in all_records if r.discovered_type == "pagination"})
    discarded_urls = sorted({r.discovered_url for r in all_records if r.discovered_type == "discarded"})

    (DISCOVERY_DIR / "discovery_records.json").write_text(
        json.dumps(
            {
                "source_name": "autocasion_profesional",
                "source_url": START_URL,
                "scrape_date": ts,
                "records": [asdict(r) for r in all_records],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    (DISCOVERY_DIR / "dealer_detail_urls.json").write_text(
        json.dumps(
            {
                "source_name": "autocasion_profesional",
                "source_url": START_URL,
                "scrape_date": ts,
                "count": len(detail_urls),
                "urls": detail_urls,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    (DISCOVERY_DIR / "province_urls.json").write_text(
        json.dumps(
            {
                "source_name": "autocasion_profesional",
                "source_url": START_URL,
                "scrape_date": ts,
                "count": len(province_urls),
                "urls": province_urls,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    (DISCOVERY_DIR / "pagination_urls.json").write_text(
        json.dumps(
            {
                "source_name": "autocasion_profesional",
                "source_url": START_URL,
                "scrape_date": ts,
                "count": len(pagination_urls),
                "urls": pagination_urls,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    (DISCOVERY_DIR / "discarded_urls.json").write_text(
        json.dumps(
            {
                "source_name": "autocasion_profesional",
                "source_url": START_URL,
                "scrape_date": ts,
                "count": len(discarded_urls),
                "urls": discarded_urls,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    (DISCOVERY_DIR / "visited_pages.json").write_text(
        json.dumps(
            {
                "source_name": "autocasion_profesional",
                "source_url": START_URL,
                "scrape_date": ts,
                "count": len(visited_pages),
                "urls": visited_pages,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )



def run(args: argparse.Namespace) -> int:
    ensure_dirs()
    pages_log = Logger(LOGS_DIR / "pages_visited.log")
    errors_log = Logger(LOGS_DIR / "errors.log")
    summary_path = LOGS_DIR / "run_summary.json"

    all_records: list[DiscoveryRecord] = []
    visited_pages: list[str] = []
    existing_detail_urls = load_existing_detail_urls() if args.resume else set()

    sb = sb_cdp.Chrome(headless=not args.headed, incognito=args.incognito)
    try:
        for page_num in range(args.start_page, args.end_page + 1):
            url = START_URL if page_num == 1 else f"{START_URL}?page={page_num}"
            try:
                print(f"[INFO] Visiting page {page_num}: {url}")
                pages_log.write(url)
                visited_pages.append(url)
                sb.get(url)
                time.sleep(args.sleep_seconds)
                html = sb.get_page_source()
                if args.save_snapshots:
                    save_snapshot(url, html)
                records = extract_links(url, html)
                all_records.extend(records)
                current_details = {r.discovered_url for r in records if r.discovered_type == 'detail'}
                new_details = current_details - existing_detail_urls
                existing_detail_urls.update(current_details)
                print(
                    f"[INFO] Page {page_num}: links={len(records)} detail_new={len(new_details)} detail_total={len(existing_detail_urls)}"
                )
                if args.stop_on_empty and not new_details and page_num > args.start_page:
                    print("[INFO] No new detail URLs on this page. Stopping by stop_on_empty rule.")
                    break
            except Exception as exc:
                errors_log.write(f"{url} :: {type(exc).__name__} :: {exc}")
                print(f"[ERROR] {url} -> {exc}")
                if args.stop_on_error:
                    raise
                continue
    finally:
        try:
            time.sleep(1.0)
            if getattr(sb, "driver", None):
                sb.driver.stop()
        except Exception:
            pass

    deduped = unique_records(all_records)
    save_outputs(deduped, visited_pages)

    summary = {
        "source_name": "autocasion_profesional",
        "source_url": START_URL,
        "scrape_date": datetime.now().strftime("%Y-%m-%d"),
        "visited_pages": len(visited_pages),
        "discovery_records": len(deduped),
        "detail_urls": len({r.discovered_url for r in deduped if r.discovered_type == "detail"}),
        "province_urls": len({r.discovered_url for r in deduped if r.discovered_type == "province"}),
        "pagination_urls": len({r.discovered_url for r in deduped if r.discovered_type == "pagination"}),
        "discarded_urls": len({r.discovered_url for r in deduped if r.discovered_type == "discarded"}),
        "strategy": "pagination_first",
        "range": {"start_page": args.start_page, "end_page": args.end_page},
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[INFO] Discovery completed.")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discovery de Autocasión Profesional por paginación")
    parser.add_argument("--start-page", type=int, default=1, help="Página inicial")
    parser.add_argument("--end-page", type=int, default=10, help="Página final")
    parser.add_argument("--sleep-seconds", type=float, default=3.0, help="Espera tras cargar página")
    parser.add_argument("--headed", action="store_true", help="Abrir navegador visible")
    parser.add_argument("--incognito", action="store_true", help="Usar modo incógnito")
    parser.add_argument("--save-snapshots", action="store_true", help="Guardar HTML de cada página visitada")
    parser.add_argument("--resume", action="store_true", help="Reutilizar detail URLs ya descubiertas")
    parser.add_argument("--stop-on-empty", action="store_true", help="Parar si una página no aporta fichas nuevas")
    parser.add_argument("--stop-on-error", action="store_true", help="Parar en el primer error")
    return parser


if __name__ == "__main__":
    raise SystemExit(run(build_parser().parse_args()))
