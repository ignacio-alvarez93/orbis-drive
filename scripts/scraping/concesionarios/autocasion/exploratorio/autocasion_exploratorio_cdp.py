#!/usr/bin/env python3
"""Scraper exploratorio de Autocasión Profesional usando SeleniumBase Pure CDP.

Objetivo:
- Abrir páginas con SeleniumBase CDP.
- Obtener HTML con get_page_source().
- Parsear el HTML con BeautifulSoup.
- Construir un dict exploratorio RAW sin normalizar ni inferir.

Notas:
- Este script es conservador por diseño.
- Extrae solo lo que vea en el HTML.
- Las heurísticas de parseo están pensadas para fase exploratoria, no para verdad final.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

try:
    from seleniumbase import sb_cdp
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "No se pudo importar seleniumbase. Instala dependencias con: "
        "pip install seleniumbase beautifulsoup4 lxml"
    ) from exc


BASE_URL = "https://www.autocasion.com"
SOURCE_URL = "https://www.autocasion.com/profesional"
SOURCE_NAME = "autocasion_profesional"

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?34[\s.-]?)?(?:\d[\s.-]?){9,}")
POSTAL_RE = re.compile(r"\b(?:0[1-9]|[1-4]\d|5[0-2])\d{3}\b")
WHITESPACE_RE = re.compile(r"\s+")

SOCIAL_HOSTS = {
    "instagram.com": "instagram_raw",
    "facebook.com": "facebook_raw",
    "tiktok.com": "tiktok_raw",
    "youtube.com": "youtube_raw",
    "youtu.be": "youtube_raw",
    "google.com": "google_business_profile_raw",
    "g.page": "google_business_profile_raw",
}


@dataclass
class RawDealerRecord:
    record_external_id: str | None
    dealer_name_raw: str | None
    dealer_type_raw: str | None
    address_raw: str | None
    location_raw: str | None
    postal_code_raw: str | None
    phone_raw: str | None
    email_raw: str | None
    website_raw: str | None
    instagram_raw: str | None
    facebook_raw: str | None
    tiktok_raw: str | None
    youtube_raw: str | None
    google_business_profile_raw: str | None
    brands_raw: list[str]
    description_raw: str | None
    source_row_url: str
    raw_payload: dict


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "message": record.getMessage(),
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if hasattr(record, "extra_payload"):
            payload.update(record.extra_payload)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(log_dir: Path) -> tuple[logging.Logger, logging.Logger]:
    log_dir.mkdir(parents=True, exist_ok=True)

    run_logger = logging.getLogger("autocasion.run")
    run_logger.setLevel(logging.INFO)
    run_logger.handlers.clear()

    error_logger = logging.getLogger("autocasion.error")
    error_logger.setLevel(logging.INFO)
    error_logger.handlers.clear()

    run_handler = logging.FileHandler(log_dir / "pages_visited.log", encoding="utf-8")
    run_handler.setFormatter(JsonFormatter())
    run_logger.addHandler(run_handler)

    err_handler = logging.FileHandler(log_dir / "errors.log", encoding="utf-8")
    err_handler.setFormatter(JsonFormatter())
    error_logger.addHandler(err_handler)

    return run_logger, error_logger


def clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = WHITESPACE_RE.sub(" ", value).strip()
    return value or None


def text_list(nodes: Iterable) -> list[str]:
    results: list[str] = []
    for node in nodes:
        text = clean_text(node.get_text(" ", strip=True))
        if text:
            results.append(text)
    return results


def unique_keep_order(values: Iterable[Optional[str]]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if not value:
            continue
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def ensure_url(href: Optional[str], base: str = BASE_URL) -> Optional[str]:
    if not href:
        return None
    return urljoin(base, href)


def domain_of(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:
        return None


def detect_external_id(url: str, soup: BeautifulSoup) -> Optional[str]:
    canonical = soup.find("link", rel=lambda v: v and "canonical" in v)
    if canonical and canonical.get("href"):
        return canonical["href"].rstrip("/").split("/")[-1]
    return url.rstrip("/").split("/")[-1] or None


def extract_socials(urls: Iterable[str]) -> dict[str, Optional[str]]:
    result = {
        "instagram_raw": None,
        "facebook_raw": None,
        "tiktok_raw": None,
        "youtube_raw": None,
        "google_business_profile_raw": None,
    }
    for url in urls:
        host = domain_of(url)
        if not host:
            continue
        for known_host, field in SOCIAL_HOSTS.items():
            if host == known_host or host.endswith(f".{known_host}"):
                if result[field] is None:
                    result[field] = url
    return result


def maybe_pick_website(urls: Iterable[str]) -> Optional[str]:
    for url in urls:
        host = domain_of(url)
        if not host:
            continue
        is_internal = host.endswith("autocasion.com")
        is_social = any(host == h or host.endswith(f".{h}") for h in SOCIAL_HOSTS)
        if not is_internal and not is_social:
            return url
    return None


def extract_emails(text: str, soup: BeautifulSoup) -> Optional[str]:
    emails = EMAIL_RE.findall(text)
    if emails:
        return unique_keep_order(emails)[0]
    mailto = soup.find("a", href=lambda v: v and v.startswith("mailto:"))
    if mailto:
        href = mailto.get("href", "")
        return clean_text(href.replace("mailto:", "", 1).split("?")[0])
    return None


def extract_phones(text: str, soup: BeautifulSoup) -> Optional[str]:
    values = PHONE_RE.findall(text)
    tel_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("tel:"):
            tel_links.append(href.replace("tel:", "", 1).strip())
    all_values = unique_keep_order(values + tel_links)
    return " | ".join(all_values) if all_values else None


def extract_postal_code(text: str) -> Optional[str]:
    match = POSTAL_RE.search(text)
    return match.group(0) if match else None


def find_json_ld_blocks(soup: BeautifulSoup) -> list[dict]:
    blocks: list[dict] = []
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.string or script.get_text("\n", strip=True)
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                blocks.extend([item for item in parsed if isinstance(item, dict)])
            elif isinstance(parsed, dict):
                blocks.append(parsed)
        except Exception:
            continue
    return blocks


def extract_from_jsonld(blocks: list[dict]) -> dict:
    payload: dict[str, Optional[str] | list[str] | dict] = {
        "dealer_name_raw": None,
        "address_raw": None,
        "postal_code_raw": None,
        "phone_raw": None,
        "email_raw": None,
        "website_raw": None,
        "description_raw": None,
        "brands_raw": [],
        "location_raw": None,
        "raw_jsonld": blocks,
    }
    for block in blocks:
        block_type = block.get("@type")
        if isinstance(block_type, list):
            block_type = ",".join(block_type)
        if block_type and any(x in str(block_type).lower() for x in ["autodealer", "automotiv", "localbusiness", "organization"]):
            payload["dealer_name_raw"] = payload["dealer_name_raw"] or clean_text(block.get("name"))
            payload["description_raw"] = payload["description_raw"] or clean_text(block.get("description"))
            payload["phone_raw"] = payload["phone_raw"] or clean_text(block.get("telephone"))
            payload["email_raw"] = payload["email_raw"] or clean_text(block.get("email"))
            payload["website_raw"] = payload["website_raw"] or clean_text(block.get("url"))

            address = block.get("address") if isinstance(block.get("address"), dict) else None
            if address:
                address_parts = [
                    clean_text(address.get("streetAddress")),
                    clean_text(address.get("postalCode")),
                    clean_text(address.get("addressLocality")),
                    clean_text(address.get("addressRegion")),
                    clean_text(address.get("addressCountry")),
                ]
                payload["address_raw"] = payload["address_raw"] or clean_text(", ".join([p for p in address_parts if p]))
                payload["postal_code_raw"] = payload["postal_code_raw"] or clean_text(address.get("postalCode"))
                loc = ", ".join([p for p in [clean_text(address.get("addressLocality")), clean_text(address.get("addressRegion")), clean_text(address.get("addressCountry"))] if p])
                payload["location_raw"] = payload["location_raw"] or clean_text(loc)

            brand = block.get("brand")
            brands: list[str] = []
            if isinstance(brand, list):
                for item in brand:
                    if isinstance(item, dict):
                        brands.append(clean_text(item.get("name")) or "")
                    else:
                        brands.append(clean_text(str(item)) or "")
            elif isinstance(brand, dict):
                brands.append(clean_text(brand.get("name")) or "")
            elif brand:
                brands.append(clean_text(str(brand)) or "")
            payload["brands_raw"] = unique_keep_order(payload["brands_raw"] + brands)
    return payload


def extract_brands_from_html(soup: BeautifulSoup) -> list[str]:
    candidates: list[str] = []
    selectors = [
        "[class*='brand']",
        "[class*='marca']",
        "[id*='brand']",
        "[id*='marca']",
        "a[href*='/coches/']",
    ]
    for selector in selectors:
        for node in soup.select(selector):
            text = clean_text(node.get_text(" ", strip=True))
            if not text:
                continue
            if len(text) > 40:
                continue
            candidates.append(text)
    return unique_keep_order(candidates)[:30]


def extract_address_candidates(soup: BeautifulSoup) -> list[str]:
    candidates: list[str] = []
    selectors = [
        "address",
        "[itemprop='address']",
        "[class*='address']",
        "[class*='direccion']",
        "[id*='address']",
        "[id*='direccion']",
    ]
    for selector in selectors:
        for node in soup.select(selector):
            text = clean_text(node.get_text(" ", strip=True))
            if text and len(text) >= 8:
                candidates.append(text)
    return unique_keep_order(candidates)


def extract_name(soup: BeautifulSoup) -> Optional[str]:
    title_tag = soup.find(["h1", "h2"])
    og_title = soup.find("meta", property="og:title")
    title = clean_text(title_tag.get_text(" ", strip=True)) if title_tag else None
    og_value = clean_text(og_title.get("content")) if og_title else None
    if title and len(title) <= 140:
        return title
    return og_value


def extract_description(soup: BeautifulSoup) -> Optional[str]:
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return clean_text(meta.get("content"))
    selectors = ["[class*='description']", "[class*='descripcion']", "article", "main p"]
    for selector in selectors:
        for node in soup.select(selector):
            text = clean_text(node.get_text(" ", strip=True))
            if text and len(text) > 40:
                return text
    return None


def extract_dealer_type(soup: BeautifulSoup, page_text: str) -> Optional[str]:
    selectors = ["[class*='badge']", "[class*='tipo']", "[class*='dealer']", "[class*='profesional']"]
    bucket: list[str] = []
    for selector in selectors:
        for node in soup.select(selector):
            text = clean_text(node.get_text(" ", strip=True))
            if text and len(text) <= 40:
                bucket.append(text)
    if bucket:
        return " | ".join(unique_keep_order(bucket)[:5])
    if "profesional" in page_text.lower():
        return "profesional"
    return None


def extract_raw_payload(soup: BeautifulSoup) -> dict:
    all_links = [ensure_url(a.get("href")) for a in soup.find_all("a", href=True)]
    all_links = unique_keep_order(all_links)
    return {
        "title": clean_text(soup.title.string if soup.title else None),
        "canonical_url": ensure_url((soup.find("link", rel=lambda v: v and "canonical" in v) or {}).get("href")) if soup.find("link", rel=lambda v: v and "canonical" in v) else None,
        "meta_description": clean_text((soup.find("meta", attrs={"name": "description"}) or {}).get("content")) if soup.find("meta", attrs={"name": "description"}) else None,
        "h1": clean_text((soup.find("h1") or {}).get_text(" ", strip=True)) if soup.find("h1") else None,
        "detected_links": all_links,
        "jsonld_count": len(find_json_ld_blocks(soup)),
    }


def parse_dealer_page(page_source: str, source_url: str) -> RawDealerRecord:
    soup = BeautifulSoup(page_source, "lxml")
    page_text = clean_text(soup.get_text(" ", strip=True)) or ""
    jsonld_blocks = find_json_ld_blocks(soup)
    jsonld = extract_from_jsonld(jsonld_blocks)

    detected_links = [ensure_url(a.get("href")) for a in soup.find_all("a", href=True)]
    detected_links = unique_keep_order(detected_links)
    socials = extract_socials(detected_links)
    website = jsonld["website_raw"] or maybe_pick_website(detected_links)

    address_candidates = extract_address_candidates(soup)
    address_raw = jsonld["address_raw"] or (address_candidates[0] if address_candidates else None)
    postal_code_raw = jsonld["postal_code_raw"] or extract_postal_code(address_raw or page_text)

    location_raw = jsonld["location_raw"]
    if not location_raw and address_raw:
        location_raw = address_raw

    brands_raw = jsonld["brands_raw"] or extract_brands_from_html(soup)

    raw_payload = extract_raw_payload(soup)
    raw_payload["jsonld"] = jsonld.get("raw_jsonld", [])
    raw_payload["address_candidates"] = address_candidates

    record = RawDealerRecord(
        record_external_id=detect_external_id(source_url, soup),
        dealer_name_raw=jsonld["dealer_name_raw"] or extract_name(soup),
        dealer_type_raw=extract_dealer_type(soup, page_text),
        address_raw=address_raw,
        location_raw=location_raw,
        postal_code_raw=postal_code_raw,
        phone_raw=jsonld["phone_raw"] or extract_phones(page_text, soup),
        email_raw=jsonld["email_raw"] or extract_emails(page_text, soup),
        website_raw=website,
        instagram_raw=socials["instagram_raw"],
        facebook_raw=socials["facebook_raw"],
        tiktok_raw=socials["tiktok_raw"],
        youtube_raw=socials["youtube_raw"],
        google_business_profile_raw=socials["google_business_profile_raw"],
        brands_raw=brands_raw,
        description_raw=jsonld["description_raw"] or extract_description(soup),
        source_row_url=source_url,
        raw_payload=raw_payload,
    )
    return record


def save_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_urls(args: argparse.Namespace) -> list[str]:
    urls: list[str] = []
    if args.url:
        urls.extend(args.url)
    if args.urls_file:
        for line in Path(args.urls_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    if not urls:
        urls.append(SOURCE_URL)
    return unique_keep_order(urls)


def fetch_page_source(sb, url: str, wait_seconds: float, snapshots_dir: Path) -> str:
    sb.get(url)
    sb.sleep(wait_seconds)
    source = sb.get_page_source()
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"snapshot_{timestamp}_{re.sub(r'[^a-zA-Z0-9]+', '_', url)[:80]}.html"
    save_text(snapshots_dir / filename, source)
    return source


def make_output_skeleton() -> dict:
    return {
        "source_name": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "scrape_date": time.strftime("%Y-%m-%d"),
        "records": [],
    }


def run(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir)
    logs_dir = output_dir / "logs"
    snapshots_dir = output_dir / "snapshots"
    output_json = output_dir / "raw_exploratorio_autocasion.json"
    timeouts_log = logs_dir / "timeouts.log"
    failed_log = logs_dir / "failed_detail_urls.log"
    summary_json = logs_dir / "run_summary.json"

    output_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    run_logger, error_logger = setup_logging(logs_dir)

    urls = load_urls(args)
    payload = make_output_skeleton()

    processed = 0
    failed = 0

    browser_kwargs = {
        "incognito": args.incognito,
        "locale": args.locale,
        "headed": args.headed,
    }
    if args.agent:
        browser_kwargs["agent"] = args.agent

    sb = None
    try:
        sb = sb_cdp.Chrome(url=None, **browser_kwargs)
        for url in urls:
            processed += 1
            try:
                run_logger.info(
                    "visit",
                    extra={"extra_payload": {"url": url, "index": processed}},
                )
                source = fetch_page_source(
                    sb=sb,
                    url=url,
                    wait_seconds=args.wait,
                    snapshots_dir=snapshots_dir,
                )
                record = parse_dealer_page(source, url)
                payload["records"].append(asdict(record))
            except Exception as exc:
                failed += 1
                msg = f"{url}\t{type(exc).__name__}: {exc}"
                save_text(failed_log, (failed_log.read_text(encoding="utf-8") if failed_log.exists() else "") + msg + "\n")
                if "timeout" in str(exc).lower():
                    save_text(timeouts_log, (timeouts_log.read_text(encoding="utf-8") if timeouts_log.exists() else "") + msg + "\n")
                error_logger.error(
                    "error",
                    extra={"extra_payload": {"url": url, "error_type": type(exc).__name__, "error": str(exc)}},
                )

    finally:
        if sb is not None:
            try:
                sb.driver.stop()
            except Exception:
                pass

    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        "source_name": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "scrape_date": time.strftime("%Y-%m-%d"),
        "processed": processed,
        "failed": failed,
        "saved_records": len(payload["records"]),
        "output_json": str(output_json),
    }
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if payload["records"] else 1


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Exploratorio Autocasión Profesional con SeleniumBase CDP + BeautifulSoup")
    parser.add_argument("--url", action="append", help="URL de ficha o listado a procesar. Se puede repetir.")
    parser.add_argument("--urls-file", help="Archivo TXT con una URL por línea.")
    parser.add_argument(
        "--output-dir",
        default="data/external/concesionarios/autocasion",
        help="Directorio base de salida.",
    )
    parser.add_argument("--wait", type=float, default=3.0, help="Segundos de espera tras abrir cada URL.")
    parser.add_argument("--locale", default="es", help="Locale del navegador para SeleniumBase.")
    parser.add_argument("--agent", help="User-Agent personalizado si quieres fijarlo.")
    parser.add_argument("--headed", action="store_true", help="Lanza Chrome visible.")
    parser.add_argument("--incognito", action="store_true", help="Lanza Chrome en incógnito.")
    return parser


if __name__ == "__main__":
    parser = build_arg_parser()
    args = parser.parse_args()
    sys.exit(run(args))
