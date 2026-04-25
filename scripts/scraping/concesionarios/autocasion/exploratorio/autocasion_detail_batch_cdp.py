#!/usr/bin/env python3
# V6_WEBSITE_PRIORITY_FIX
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from seleniumbase import sb_cdp

SOURCE_NAME = "autocasion_profesional"
SOURCE_URL = "https://www.autocasion.com/profesional"
ROOT = Path("data/external/concesionarios/autocasion")
LOGS_DIR = ROOT / "logs"
SNAPSHOTS_DIR = ROOT / "snapshots"
DISCOVERY_DIR = ROOT / "discovery"
RAW_OUTPUT = ROOT / "raw_exploratorio_autocasion.json"
DETAIL_RESULTS_OUTPUT = ROOT / "detail_results.json"
RUN_SUMMARY = LOGS_DIR / "run_summary.json"
FAILED_DETAIL = LOGS_DIR / "failed_detail_urls.log"
GLOBAL_EXCLUDED_HOST_FRAGMENTS = {
    "autocasion.com", "vocento", "sumauto", "facebook.com", "instagram.com",
    "tiktok.com", "youtube.com", "youtu.be", "linkedin.com", "twitter.com",
    "x.com", "play.google.com", "itunes.apple.com", "apps.apple.com",
}

def ensure_dirs() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    DISCOVERY_DIR.mkdir(parents=True, exist_ok=True)

def clean_text(value: Any) -> Optional[str]:
    if value is None or isinstance(value, (dict, list, tuple, set)):
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None

def absolutize_links(base_url: str, links: List[str]) -> List[str]:
    out, seen = [], set()
    for href in links:
        if not href:
            continue
        href = href.strip()
        if not href or href.startswith("javascript:") or href == "#":
            continue
        full = urljoin(base_url, href)
        if full not in seen:
            seen.add(full)
            out.append(full)
    return out

def extract_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    return absolutize_links(base_url, [a.get("href") for a in soup.find_all("a", href=True)])

def extract_title(soup: BeautifulSoup) -> Optional[str]:
    return clean_text(soup.title.string) if soup.title and soup.title.string else None

def extract_meta_description(soup: BeautifulSoup) -> Optional[str]:
    tag = soup.find("meta", attrs={"name": "description"})
    return clean_text(tag.get("content")) if tag and tag.get("content") else None

def extract_h1(soup: BeautifulSoup) -> Optional[str]:
    h1 = soup.find("h1")
    return clean_text(h1.get_text(" ", strip=True)) if h1 else None

def parse_jsonld(soup: BeautifulSoup) -> List[Any]:
    objs: List[Any] = []
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = tag.string or tag.get_text(" ", strip=True)
        if not raw:
            continue
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                objs.extend(data)
            else:
                objs.append(data)
        except Exception:
            continue
    return objs

def walk_find(obj: Any, key: str) -> List[Any]:
    found: List[Any] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                found.append(v)
            found.extend(walk_find(v, key))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(walk_find(item, key))
    return found

def host_is_excluded(host: str) -> bool:
    host = (host or "").lower()
    return any(fragment in host for fragment in GLOBAL_EXCLUDED_HOST_FRAGMENTS)

def extract_urls_from_text(text: Optional[str]) -> List[str]:
    if not text:
        return []
    return re.findall(r'https?://[^\s<>"\')]+', text)

def is_valid_external_website(url: str) -> bool:
    try:
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        return bool(host) and not host_is_excluded(host) and parsed.scheme in {"http", "https"}
    except Exception:
        return False

def pick_best_external_website(links: List[str], description_raw: Optional[str]) -> Optional[str]:
    for url in extract_urls_from_text(description_raw):
        if is_valid_external_website(url):
            return url
    for link in links:
        if is_valid_external_website(link):
            return link
    return None

def first_match(patterns: List[str], text: str) -> Optional[str]:
    for pat in patterns:
        m = re.search(pat, text, flags=re.I)
        if m:
            return clean_text(m.group(1))
    return None

def extract_visible_text(soup: BeautifulSoup) -> str:
    for bad in soup(["script", "style", "noscript"]):
        bad.extract()
    return clean_text(soup.get_text("\n", strip=True)) or ""

def extract_dealer_from_jsonld(jsonlds: List[Any]) -> Dict[str, Any]:
    out = {"dealer_name_raw": None, "address_raw": None, "location_raw": None, "postal_code_raw": None, "phone_raw": None, "email_raw": None, "description_raw": None}
    for obj in jsonlds:
        flat_types = {str(t).lower() for t in walk_find(obj, "@type") if isinstance(t, str)}
        if {"autodealer", "organization", "localbusiness"} & flat_types:
            names, descs = walk_find(obj, "name"), walk_find(obj, "description")
            phones, emails, addresses = walk_find(obj, "telephone"), walk_find(obj, "email"), walk_find(obj, "address")
            if not out["dealer_name_raw"]:
                out["dealer_name_raw"] = next((clean_text(n) for n in names if clean_text(n)), None)
            if not out["description_raw"]:
                out["description_raw"] = next((clean_text(d) for d in descs if clean_text(d)), None)
            if not out["phone_raw"]:
                out["phone_raw"] = next((clean_text(p) for p in phones if clean_text(p)), None)
            if not out["email_raw"]:
                out["email_raw"] = next((clean_text(e) for e in emails if clean_text(e)), None)
            if addresses:
                addr = addresses[0]
                if isinstance(addr, dict):
                    street = clean_text(addr.get("streetAddress"))
                    locality = clean_text(addr.get("addressLocality"))
                    postal = clean_text(addr.get("postalCode"))
                    country = addr.get("addressCountry")
                    country = clean_text(country.get("name")) if isinstance(country, dict) else clean_text(country)
                    parts = [p for p in [street, locality, postal, country] if p]
                    if parts:
                        out["address_raw"] = ", ".join(parts)
                    if locality or country:
                        out["location_raw"] = ", ".join([p for p in [locality, country] if p])
                    out["postal_code_raw"] = postal
            break
    return out

def extract_visible_fields(soup: BeautifulSoup, page_text: str) -> Dict[str, Any]:
    meta_desc = extract_meta_description(soup)
    out = {
        "dealer_name_raw": extract_h1(soup),
        "description_raw": meta_desc,
        "phone_raw": first_match([r'(\+?\d[\d\-\s]{7,}\d)'], page_text),
        "email_raw": first_match([r'([A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,})'], page_text),
        "postal_code_raw": first_match([r'\b(\d{5})\b'], page_text),
        "address_raw": None,
        "location_raw": None,
    }
    out["address_raw"] = first_match([
        r'(C\/[^.\n]+?\b\d{5}\b[^.\n]*)', r'(Calle [^.\n]+?\b\d{5}\b[^.\n]*)',
        r'(Avenida [^.\n]+?\b\d{5}\b[^.\n]*)', r'(Av\. [^.\n]+?\b\d{5}\b[^.\n]*)',
        r'(Pol[ií]gono [^.\n]+?\b\d{5}\b[^.\n]*)'
    ], page_text)
    if out["address_raw"]:
        out["location_raw"] = first_match([r',\s*([^,]+),\s*\d{5},\s*[A-Z]{2}\b', r',\s*([^,]+),\s*\d{5}\b'], out["address_raw"])
    return out

def merge_fields(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(primary)
    for k, v in secondary.items():
        if not merged.get(k) and v:
            merged[k] = v
    return merged

def detect_minimum_signals(record: Dict[str, Any], page_text: str) -> List[str]:
    signals = [f for f in ["dealer_name_raw", "phone_raw", "address_raw", "location_raw", "website_raw", "email_raw"] if record.get(f)]
    if re.search(r'\b(stock|veh[íi]culos|coches|ocasi[oó]n|segunda mano)\b', page_text, flags=re.I):
        signals.append("context:stock")
    return signals

def extract_brand_values(soup: BeautifulSoup) -> List[str]:
    vals = []
    for tag in soup.find_all(string=re.compile(r"Marca", re.I)):
        t = clean_text(tag)
        if t and t.lower() not in {"marca todas", "todas", "todas las marcas"}:
            vals.append(t)
    return vals

def maybe_snapshot(html: str, url: str) -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r"[^a-zA-Z0-9]+", "_", url)[:120].strip("_")
    (SNAPSHOTS_DIR / f"snapshot_{ts}_{safe}.html").write_text(html, encoding="utf-8", errors="ignore")

def read_input_urls() -> List[str]:
    payload = json.loads((DISCOVERY_DIR / "dealer_detail_urls.json").read_text(encoding="utf-8"))
    return payload.get("urls", [])

def process_one(url: str, html: str) -> Optional[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    links = extract_links(soup, url)
    jsonlds = parse_jsonld(soup)
    page_text = extract_visible_text(soup)
    merged = merge_fields(extract_dealer_from_jsonld(jsonlds), extract_visible_fields(soup, page_text))
    description_raw = merged.get("description_raw") or extract_meta_description(soup)
    website_raw = pick_best_external_website(links, description_raw)
    record = {
        "record_external_id": url.rstrip("/").split("/")[-1],
        "dealer_name_raw": merged.get("dealer_name_raw"),
        "dealer_type_raw": "profesional",
        "address_raw": merged.get("address_raw"),
        "location_raw": merged.get("location_raw"),
        "postal_code_raw": merged.get("postal_code_raw"),
        "phone_raw": merged.get("phone_raw"),
        "email_raw": merged.get("email_raw"),
        "website_raw": website_raw,
        "instagram_raw": None,
        "facebook_raw": None,
        "tiktok_raw": None,
        "youtube_raw": None,
        "google_business_profile_raw": None,
        "brands_raw": extract_brand_values(soup),
        "description_raw": description_raw,
        "source_row_url": url,
        "raw_payload": {
            "title": extract_title(soup),
            "canonical_url": url,
            "meta_description": extract_meta_description(soup),
            "h1": extract_h1(soup),
            "detected_links": links,
            "jsonld_count": len(jsonlds),
            "filters_applied": {
                "global_social_filtered": True,
                "autocasion_website_filtered": True,
                "brand_placeholder_filtered": True,
                "website_priority_fix_v6": True,
            },
        },
    }
    signals = detect_minimum_signals(record, page_text)
    record["raw_payload"]["minimum_signals"] = signals
    if not any(s in signals for s in ["dealer_name_raw", "phone_raw", "address_raw", "location_raw", "email_raw"]) and "context:stock" not in signals:
        return None
    return record

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--incognito", action="store_true")
    parser.add_argument("--save-snapshots", action="store_true")
    args = parser.parse_args()
    ensure_dirs()
    urls = read_input_urls()
    if args.offset:
        urls = urls[args.offset:]
    if args.limit is not None:
        urls = urls[:args.limit]
    records, detail_results = [], []
    failed_count = 0
    start = time.time()
    sb = None
    try:
        kwargs = {}
        if args.headed: kwargs["headed"] = True
        if args.incognito: kwargs["incognito"] = True
        sb = sb_cdp.Chrome(**kwargs)
        for idx, url in enumerate(urls, start=1):
            print(f"[INFO] Visiting detail {idx}/{len(urls)}: {url}")
            try:
                sb.get(url)
                time.sleep(2.5)
                html = sb.get_page_source()
                if args.save_snapshots:
                    maybe_snapshot(html, url)
                record = process_one(url, html)
                if record is None:
                    failed_count += 1
                    with FAILED_DETAIL.open("a", encoding="utf-8") as fh: fh.write(f"{url}\tinvalid_minimum_signals\n")
                    detail_results.append({"url": url, "status": "failed"})
                    continue
                records.append(record)
                detail_results.append({"url": url, "status": "accepted"})
                print(f"[INFO] Detail accepted: id={record['record_external_id']} name='{record.get('dealer_name_raw')}'")
            except Exception as exc:
                failed_count += 1
                with FAILED_DETAIL.open("a", encoding="utf-8") as fh: fh.write(f"{url}\texception:{type(exc).__name__}\n")
                detail_results.append({"url": url, "status": "failed", "error": type(exc).__name__})
    finally:
        if sb is not None:
            try:
                time.sleep(1)
                sb.driver.stop()
            except Exception:
                pass
    RAW_OUTPUT.write_text(json.dumps({"source_name": SOURCE_NAME, "source_url": SOURCE_URL, "scrape_date": str(date.today()), "records": records}, ensure_ascii=False, indent=2), encoding="utf-8")
    DETAIL_RESULTS_OUTPUT.write_text(json.dumps(detail_results, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {"source_name": SOURCE_NAME, "source_url": SOURCE_URL, "scrape_date": str(date.today()), "input_urls": len(urls), "records_accepted": len(records), "records_failed": failed_count, "output_file": str(RAW_OUTPUT), "detail_results_file": str(DETAIL_RESULTS_OUTPUT), "elapsed_seconds": round(time.time() - start, 2), "offset": args.offset, "limit": args.limit}
    RUN_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[INFO] Batch detail extraction completed.")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
