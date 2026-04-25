from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from bs4 import BeautifulSoup


BASE_DIR = Path("data/external/concesionarios/cochesnet")
HTML_DIR = BASE_DIR / "html"
OUTPUT_JSON = BASE_DIR / "detail_results.json"


def read_html_with_fallback(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def safe_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = unescape(value).replace("\xa0", " ").strip()
    return value or None


def extract_slug_from_canonical(canonical_url: str | None) -> str | None:
    if not canonical_url:
        return None
    m = re.search(r"/concesionario/([^/]+)/?", canonical_url)
    return m.group(1) if m else None


def clean_logo_alt(logo_alt: str | None) -> str | None:
    if not logo_alt:
        return None
    text = safe_text(logo_alt)
    if not text:
        return None
    text = re.sub(r"^logo de\s+", "", text, flags=re.IGNORECASE)
    return text or None


def extract_name_fallback(soup: BeautifulSoup) -> str | None:
    selectors = [
        "h1",
        ".mt-HeroDealer-title",
        ".mt-HeroDealer-name",
        '[data-testid="dealer-name"]',
        "meta[property='og:title']",
        "title",
    ]
    for sel in selectors:
        node = soup.select_one(sel)
        if not node:
            continue
        if node.name == "meta":
            text = node.get("content")
        else:
            text = node.get_text(" ", strip=True)
        text = safe_text(text)
        if text and len(text) > 1:
            return text
    return None


def parse_google_maps_destination(maps_url: str | None) -> dict[str, Any]:
    result = {
        "address_raw": None,
        "postal_code_raw": None,
        "location_raw": None,
        "maps_destination_raw": None,
    }

    if not maps_url:
        return result

    parsed = urlparse(maps_url)
    qs = parse_qs(parsed.query)
    destination = qs.get("destination", [None])[0]
    if not destination:
        return result

    destination = safe_text(unquote(destination))
    result["maps_destination_raw"] = destination
    result["address_raw"] = destination

    postal_match = re.search(r"\b(\d{5})\b", destination or "")
    if postal_match:
        result["postal_code_raw"] = postal_match.group(1)

    if result["postal_code_raw"] and destination:
        split_match = re.split(rf"\b{re.escape(result['postal_code_raw'])}\b", destination, maxsplit=1)
        if len(split_match) == 2:
            tail = split_match[1].strip(" ,.")
            result["location_raw"] = tail or None

    return result


def extract_address_text_fallback(soup: BeautifulSoup) -> str | None:
    node = soup.select_one(".mt-HeroDealer-containerInfoAddress")
    if not node:
        return None

    title = node.get("title")
    if title:
        return safe_text(title)

    text = safe_text(node.get_text(" ", strip=True))
    if text and text.lower() != "cómo llegar":
        return text

    return None


def extract_possible_website(soup: BeautifulSoup) -> str | None:
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href.startswith("http"):
            continue
        lowered = href.lower()
        if "coches.net" in lowered:
            continue
        if "google.com/maps" in lowered:
            continue
        if "carfax.es" in lowered:
            continue
        if "fotocasa.es" in lowered:
            continue
        return href
    return None


def extract_possible_email(soup: BeautifulSoup) -> str | None:
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().startswith("mailto:"):
            return href[len("mailto:"):].strip() or None
    return None


def extract_possible_phone(soup: BeautifulSoup) -> str | None:
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().startswith("tel:"):
            return href[len("tel:"):].strip() or None
    return None


def extract_social_links(soup: BeautifulSoup) -> dict[str, str | None]:
    result = {
        "instagram_raw": None,
        "facebook_raw": None,
        "tiktok_raw": None,
        "youtube_raw": None,
    }

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        lowered = href.lower()

        if result["instagram_raw"] is None and "instagram.com" in lowered:
            result["instagram_raw"] = href
        elif result["facebook_raw"] is None and "facebook.com" in lowered:
            result["facebook_raw"] = href
        elif result["tiktok_raw"] is None and "tiktok.com" in lowered:
            result["tiktok_raw"] = href
        elif result["youtube_raw"] is None and ("youtube.com" in lowered or "youtu.be" in lowered):
            result["youtube_raw"] = href

    return result


def extract_description(soup: BeautifulSoup) -> str | None:
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return safe_text(meta["content"])
    return None


def extract_brands_raw(soup: BeautifulSoup) -> list[str]:
    brands: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip().lower()
        text = safe_text(a.get_text(" ", strip=True))
        if not text:
            continue
        if "/concesionarios/" in href and 1 < len(text) < 50 and text not in brands:
            brands.append(text)
    return brands


def parse_detail_file(path: Path) -> dict[str, Any] | None:
    html = read_html_with_fallback(path)
    soup = BeautifulSoup(html, "html.parser")

    canonical_tag = soup.select_one('link[rel="canonical"]')
    canonical_url = canonical_tag.get("href") if canonical_tag else None

    if not canonical_url or "/concesionario/" not in canonical_url:
        return None

    logo = soup.select_one(".mt-HeroDealer-logo")
    logo_alt = logo.get("alt") if logo else None

    address_anchor = soup.select_one(".mt-HeroDealer-containerInfoAddress")
    address_href = address_anchor.get("href") if address_anchor else None
    address_text = extract_address_text_fallback(soup)

    maps_data = parse_google_maps_destination(address_href)

    dealer_name_raw = clean_logo_alt(logo_alt) or extract_name_fallback(soup)
    address_raw = maps_data["address_raw"] or address_text

    website_raw = extract_possible_website(soup)
    email_raw = extract_possible_email(soup)
    phone_raw = extract_possible_phone(soup)
    socials = extract_social_links(soup)
    description_raw = extract_description(soup)
    brands_raw = extract_brands_raw(soup)

    return {
        "record_external_id": extract_slug_from_canonical(canonical_url),
        "dealer_name_raw": dealer_name_raw,
        "dealer_type_raw": None,
        "address_raw": address_raw,
        "location_raw": maps_data["location_raw"],
        "postal_code_raw": maps_data["postal_code_raw"],
        "phone_raw": phone_raw,
        "email_raw": email_raw,
        "website_raw": website_raw,
        "instagram_raw": socials["instagram_raw"],
        "facebook_raw": socials["facebook_raw"],
        "tiktok_raw": socials["tiktok_raw"],
        "youtube_raw": socials["youtube_raw"],
        "google_business_profile_raw": None,
        "brands_raw": brands_raw,
        "description_raw": description_raw,
        "source_row_url": canonical_url,
        "raw_payload": {
            "source_file": str(path),
            "canonical_url": canonical_url,
            "logo_alt": logo_alt,
            "address_anchor_text": address_text,
            "address_anchor_href": address_href,
            "maps_destination_raw": maps_data["maps_destination_raw"],
        },
    }


def main() -> None:
    files = sorted(HTML_DIR.glob("*.html"), key=lambda p: p.stat().st_mtime)
    results = []

    for path in files:
        parsed = parse_detail_file(path)
        if parsed is not None:
            results.append(parsed)

    OUTPUT_JSON.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Ficheros HTML revisados: {len(files)}")
    print(f"Fichas válidas extraídas: {len(results)}")
    print(f"Salida: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
