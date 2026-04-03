
from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .field_mapping import SECTION_FIELD_MAP, SUMMARY_FIELD_MAP

PARSER_VERSION = "v3"
SCRAPER_VERSION = "v3"

NUM_RE = re.compile(r"-?\d+(?:[\.,]\d+)?")
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")


def normalize_space(text: str | None) -> str | None:
    if text is None:
        return None
    text = text.replace("\ufeff", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def parse_number(text: str | None) -> float | None:
    if not text:
        return None
    source = text.replace("\xa0", " ")
    source = source.replace(".", "").replace(",", ".")
    m = NUM_RE.search(source)
    if not m:
        return None
    try:
        return float(m.group())
    except ValueError:
        return None


def parse_int(text: str | None) -> int | None:
    value = parse_number(text)
    return int(round(value)) if value is not None else None


def slugify(text: str | None) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def canonical_upper(text: str | None) -> str | None:
    return text.upper() if text else None


def build_empty_clean(contract: dict[str, Any]) -> dict[str, Any]:
    return {field_name: None for field_name in contract["fields"].keys()}


def parse_jsonld(soup: BeautifulSoup) -> dict[str, Any]:
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = normalize_space(script.string or script.get_text())
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and "breadcrumb" in data:
            return data
    return {}


def extract_breadcrumbs(jsonld: dict[str, Any]) -> list[dict[str, Any]]:
    breadcrumb = jsonld.get("breadcrumb", {}) if isinstance(jsonld, dict) else {}
    items = breadcrumb.get("itemListElement", []) if isinstance(breadcrumb, dict) else []
    output: list[dict[str, Any]] = []
    for item in items:
        output.append(
            {
                "position": item.get("position"),
                "name": normalize_space(item.get("name")),
                "item": item.get("item"),
            }
        )
    return output


def extract_meta(soup: BeautifulSoup) -> dict[str, Any]:
    def meta(attr_name: str, attr_value: str) -> str | None:
        tag = soup.find("meta", attrs={attr_name: attr_value})
        return normalize_space(tag.get("content")) if tag and tag.get("content") else None

    canonical_tag = soup.find("link", rel="canonical")
    html_tag = soup.find("html")
    return {
        "canonical": canonical_tag.get("href") if canonical_tag else None,
        "og_title": meta("property", "og:title"),
        "og_description": meta("property", "og:description"),
        "og_url": meta("property", "og:url"),
        "meta_description": meta("name", "description"),
        "html_lang": html_tag.get("lang") if html_tag else None,
        "data_lang": html_tag.get("data-lang") if html_tag else None,
    }


def extract_summary_cards(soup: BeautifulSoup) -> dict[str, str]:
    summary: dict[str, str] = {}
    for block in soup.select("#qs .qs"):
        dt_tag = block.find("dt")
        dd_tag = block.find("dd")
        label = normalize_space(dt_tag.get("title") if dt_tag else None)
        value = normalize_space(dd_tag.get_text(" ", strip=True) if dd_tag else None)
        if label and value:
            summary[label] = value
    return summary


def extract_sections(soup: BeautifulSoup) -> dict[str, dict[str, Any]]:
    sections: dict[str, dict[str, Any]] = {}
    for section in soup.find_all("section"):
        heading_tag = section.find(["h2", "h3"])
        if not heading_tag:
            continue
        heading = normalize_space(heading_tag.get_text(" ", strip=True))
        if not heading:
            continue
        rows: dict[str, Any] = {}
        for item in section.select("dl > div.sd"):
            dt = normalize_space(item.find("dt").get_text(" ", strip=True) if item.find("dt") else None)
            if not dt:
                continue
            values = [normalize_space(dd.get_text(" ", strip=True)) for dd in item.find_all("dd")]
            values = [v for v in values if v]
            if not values:
                continue
            rows[dt] = values[0] if len(values) == 1 else values
        if rows:
            sections[heading] = rows
    return sections


def extract_section_links(soup: BeautifulSoup) -> dict[str, str | None]:
    links: dict[str, str | None] = {
        "source_manufacturer_url": None,
        "source_generation_url": None,
        "source_model_url": None,
    }
    bc = soup.select_one("#bc")
    if not bc:
        return links
    anchors = bc.find_all("a")
    if len(anchors) >= 1:
        links["source_manufacturer_url"] = anchors[0].get("href")
    if len(anchors) >= 2:
        links["source_generation_url"] = anchors[1].get("href")
        links["source_model_url"] = anchors[1].get("href")
    return links


def infer_hierarchy(meta: dict[str, Any], breadcrumbs: list[dict[str, Any]], soup: BeautifulSoup) -> dict[str, Any]:
    title = normalize_space(soup.find("h1").get_text(" ", strip=True) if soup.find("h1") else None)
    generation = breadcrumbs[1]["name"] if len(breadcrumbs) > 1 else None
    manufacturer = breadcrumbs[0]["name"] if len(breadcrumbs) > 0 else None
    version_name = None
    model_name = None
    first_year = None
    if title:
        match = re.match(r"(?P<year>\d{4})\s+(?P<manufacturer>\S+)\s+(?P<rest>.+?)\s+-\s+Ficha", title)
        if match:
            first_year = int(match.group("year"))
            manufacturer = manufacturer or match.group("manufacturer")
            rest = normalize_space(match.group("rest"))
            if rest:
                tokens = rest.split()
                model_name = tokens[0]
                version_name = normalize_space(rest[len(model_name):].strip()) or model_name
    if not model_name and len(breadcrumbs) > 1 and breadcrumbs[1]["name"]:
        model_name = breadcrumbs[1]["name"].split("(")[0].strip()
    if not version_name and len(breadcrumbs) > 2:
        trail = breadcrumbs[2]["name"]
        if trail and manufacturer and model_name:
            stripped = re.sub(rf"^\d{{4}}\s+{re.escape(manufacturer)}\s+{re.escape(model_name)}\s*", "", trail).strip()
            version_name = stripped or model_name
    return {
        "headline": title,
        "manufacturer_name": manufacturer,
        "model_name": model_name,
        "generation_name": generation,
        "version_name": version_name,
        "version_name_canonical": normalize_space(version_name),
        "generation_name_canonical": normalize_space(generation),
        "first_year": first_year,
        "full_title": meta.get("og_title") or title,
    }


def parse_production(meta_description: str | None, generation_name: str | None) -> dict[str, Any]:
    text = meta_description or ""
    years = [int(y) for y in YEAR_RE.findall(text)]
    facelift_status = None
    lowered = text.lower()
    if "actualizado" in lowered:
        facelift_status = "actualizado"
    elif "preactualizado" in lowered:
        facelift_status = "preactualizado"
    is_current = None
    if generation_name and "actualidad" in generation_name.lower():
        is_current = True
    elif years:
        is_current = years[-1] >= datetime.now().year
    return {
        "production_start_year": years[0] if years else None,
        "production_end_year": years[-1] if years else None,
        "production_years_text": f"{years[0]}-{years[-1]}" if len(years) >= 2 else None,
        "model_year": years[0] if years else None,
        "is_current_generation": is_current,
        "facelift_status": facelift_status,
    }


def split_multi_value(key: str, values: list[str]) -> dict[str, Any]:
    data: dict[str, Any] = {key: values[0]}
    if key == "Potencia Máximo" and len(values) > 1:
        data[f"{key}_bhp"] = values[1]
        if len(values) > 2:
            data[f"{key}_rpm"] = values[2]
    if key == "Par Máximo" and len(values) > 1:
        data[f"{key}_lbft"] = values[1]
        if len(values) > 2:
            data[f"{key}_rpm"] = values[2]
    if key == "Relación Diámetro-Carrera" and len(values) > 1:
        data[f"{key}_label"] = values[1]
    if key == "PME" and len(values) > 1:
        data[f"{key}_psi"] = values[1]
    if key == "Ruedas Motrices" and len(values) > 1:
        data[f"{key}_label"] = values[1]
    if key == "Cilindrada" and len(values) > 1:
        data[f"{key}_cc"] = values[1]
    if key == "Válvulas/Cilindro":
        total_match = re.search(r"\((\d+)v Total\)", values[0])
        if total_match:
            data[f"{key}_total"] = total_match.group(1)
    if key == "Diámetro x Carrera" and len(values) > 1:
        data[f"{key}_bore"] = values[0]
        data[f"{key}_stroke"] = values[1]
    if key == "Capacitad Maletero" and len(values) > 1:
        data[f"{key}_min"] = values[0]
        data[f"{key}_max"] = values[1]
    return data


def assign_contract_value(clean: dict[str, Any], field_name: str, raw_value: Any) -> None:
    if raw_value is None or field_name not in clean:
        return
    text = normalize_space(raw_value if isinstance(raw_value, str) else str(raw_value))
    if not text:
        return

    int_fields = {
        "doors", "seats", "gear_count", "production_start_year", "production_end_year",
        "max_power_cv", "max_power_bhp", "max_power_rpm", "max_torque_rpm", "engine_displacement_cc",
        "valves_per_cylinder", "valves_total", "power_cv", "power_bhp", "model_year", "cylinders",
    }
    num_fields = {
        "top_speed_kmh", "top_speed_mph", "acceleration_0_100_s", "acceleration_0_62_s",
        "fuel_consumption_combined_l_100km", "fuel_consumption_combined_mpg_uk", "fuel_consumption_combined_mpg_us",
        "co2_emissions_g_km", "engine_displacement_l", "max_torque_nm", "max_torque_lbft", "compression_ratio",
        "bore_mm", "stroke_mm", "bore_stroke_ratio", "specific_output_cv_l", "specific_output_kw_l",
        "power_per_cylinder_cv", "unitary_displacement_cc", "bmep_bar", "bmep_psi", "turning_circle_m",
        "kerb_weight_kg", "gross_weight_kg", "payload_kg", "length_mm", "width_mm", "height_mm",
        "wheelbase_mm", "front_track_mm", "rear_track_mm", "boot_capacity_l", "boot_capacity_min_l",
        "boot_capacity_max_l", "fuel_tank_l", "power_to_weight_cv_ton", "power_to_weight_kw_ton",
        "max_power_kw", "ground_clearance_mm", "width_including_mirrors_mm",
    }
    bool_fields = {"is_current_generation", "start_stop"}

    if field_name in int_fields:
        clean[field_name] = parse_int(text)
        return
    if field_name in num_fields:
        clean[field_name] = parse_number(text)
        return
    if field_name in bool_fields:
        lowered = text.lower()
        if lowered in {"sí", "si", "yes", "true", "1"}:
            clean[field_name] = True
        elif lowered in {"no", "false", "0"}:
            clean[field_name] = False
        return
    if field_name == "drive_type":
        clean[field_name] = text.lower()
        return
    clean[field_name] = text


def map_summary_data(clean: dict[str, Any], summary: dict[str, str]) -> None:
    for label, value in summary.items():
        field_name = SUMMARY_FIELD_MAP.get(label)
        if field_name:
            assign_contract_value(clean, field_name, value)


def map_section_data(clean: dict[str, Any], sections: dict[str, dict[str, Any]]) -> None:
    for section_name, rows in sections.items():
        mapping = SECTION_FIELD_MAP.get(section_name)
        if not mapping:
            continue
        for label, raw_value in rows.items():
            parsed_map = split_multi_value(label, raw_value if isinstance(raw_value, list) else [raw_value])
            for effective_label, effective_value in parsed_map.items():
                field_name = mapping.get(effective_label)
                if field_name:
                    assign_contract_value(clean, field_name, effective_value)


def enrich_derived_fields(clean: dict[str, Any], sections: dict[str, dict[str, Any]], summary: dict[str, str]) -> None:
    gearbox_label = clean.get("gearbox_label")
    if gearbox_label:
        upper = gearbox_label.upper()
        if "CVT" in upper:
            clean["gearbox_type"] = clean.get("gearbox_type") or "CVT"
        elif "AT" in upper or "AUT" in upper:
            clean["gearbox_type"] = clean.get("gearbox_type") or "AT"
        elif "DSG" in upper or "DCT" in upper:
            clean["gearbox_type"] = clean.get("gearbox_type") or "DCT"
        else:
            clean["gearbox_type"] = clean.get("gearbox_type") or "MT"
        gear_count = parse_int(gearbox_label)
        if gear_count is not None:
            clean["gear_count"] = gear_count

    if clean.get("max_power_cv") is not None and clean.get("max_power_kw") is None:
        clean["max_power_kw"] = round(clean["max_power_cv"] * 0.73549875, 1)
    if clean.get("power_cv") is not None and clean.get("power_bhp") is None:
        clean["power_bhp"] = int(round(clean["power_cv"] * 0.98632))
    if clean.get("max_power_kw") is not None and clean.get("engine_displacement_l"):
        clean["specific_output_kw_l"] = round(clean["max_power_kw"] / clean["engine_displacement_l"], 1)
    if clean.get("power_to_weight_cv_ton") is not None and clean.get("max_power_kw") is not None and clean.get("max_power_cv"):
        clean["power_to_weight_kw_ton"] = round(clean["power_to_weight_cv_ton"] * clean["max_power_kw"] / clean["max_power_cv"], 1)

    if clean.get("version_name"):
        clean["version_name_canonical"] = normalize_space(clean["version_name"])
        clean["version_name_upper"] = canonical_upper(clean["version_name"])
    if clean.get("generation_name"):
        clean["generation_name_canonical"] = normalize_space(clean["generation_name"])
        clean["generation_name_upper"] = canonical_upper(clean["generation_name"])

    if clean.get("source_model_url") is None:
        clean["source_model_url"] = clean.get("source_generation_url")

    # conservative extraction from summary when sections vary
    if clean.get("power_cv") is None and summary.get("Potencia Total"):
        clean["power_cv"] = parse_int(summary.get("Potencia Total"))
    if clean.get("max_power_cv") is None and clean.get("power_cv") is not None:
        clean["max_power_cv"] = clean["power_cv"]
    if clean.get("drive_type") is None and clean.get("drive_type_label"):
        label = str(clean["drive_type_label"]).lower()
        if "delan" in label:
            clean["drive_type"] = "fwd"
        elif "tras" in label:
            clean["drive_type"] = "rwd"
        elif "4x4" in label or "awd" in label or "total" in label:
            clean["drive_type"] = "awd"

    # cylinders from engine layout text
    layout = str(clean.get("engine_layout") or "")
    cyl_match = re.search(r"(\d+)\s*[Cc]il", layout)
    if cyl_match and clean.get("cylinders") is None:
        clean["cylinders"] = int(cyl_match.group(1))


def build_ids(clean: dict[str, Any]) -> None:
    manufacturer_slug = slugify(clean.get("manufacturer_name"))
    model_slug = slugify(clean.get("model_name"))
    generation_slug = slugify(clean.get("generation_name"))
    version_slug = slugify(clean.get("version_name"))
    clean["manufacturer_id"] = clean.get("manufacturer_id") or f"mfr_{manufacturer_slug}"
    clean["model_id"] = clean.get("model_id") or f"mdl_{manufacturer_slug}_{model_slug}"
    clean["generation_id"] = clean.get("generation_id") or f"gen_{manufacturer_slug}_{model_slug}_{generation_slug}"
    clean["version_id"] = clean.get("version_id") or f"ver_{manufacturer_slug}_{model_slug}_{generation_slug}_{version_slug}"


def minimum_required_ok(clean: dict[str, Any], contract: dict[str, Any]) -> tuple[bool, list[str]]:
    missing = [field for field in contract.get("required_minimum_fields", []) if clean.get(field) in {None, ""}]
    return (len(missing) == 0, missing)


def normalize_url(source_url: str | None, href: str | None) -> str | None:
    if not href:
        return None
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if source_url:
        parsed = urlparse(source_url)
        if href.startswith("/"):
            return f"{parsed.scheme}://{parsed.netloc}{href}"
        base = parsed.path.rsplit("/", 1)[0]
        return f"{parsed.scheme}://{parsed.netloc}{base}/{href}".replace("//es", "/es")
    return href


def parse_version_html(html: str, source_url: str | None, contract: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    jsonld = parse_jsonld(soup)
    breadcrumbs = extract_breadcrumbs(jsonld)
    meta = extract_meta(soup)
    summary = extract_summary_cards(soup)
    sections = extract_sections(soup)
    links = extract_section_links(soup)
    hierarchy = infer_hierarchy(meta, breadcrumbs, soup)
    production = parse_production(meta.get("meta_description"), hierarchy.get("generation_name"))

    clean = build_empty_clean(contract)
    clean["source"] = "encycarpedia"
    clean["source_version_url"] = source_url or meta.get("canonical") or meta.get("og_url")
    clean["source_version_url_canonical"] = meta.get("canonical")
    clean["source_generation_url"] = normalize_url(clean["source_version_url"], links.get("source_generation_url"))
    clean["source_model_url"] = normalize_url(clean["source_version_url"], links.get("source_model_url"))
    clean["source_manufacturer_url"] = normalize_url(clean["source_version_url"], links.get("source_manufacturer_url"))
    clean["scrape_timestamp"] = datetime.now(timezone.utc).isoformat()
    clean["scrape_date"] = clean["scrape_timestamp"][:10]
    clean["html_lang"] = meta.get("html_lang")
    clean["source_date_modified"] = jsonld.get("dateModified") if isinstance(jsonld, dict) else None
    clean["headline"] = hierarchy.get("headline")
    clean["full_title"] = hierarchy.get("full_title")
    clean["meta_description"] = meta.get("meta_description")
    clean["manufacturer_name"] = hierarchy.get("manufacturer_name")
    clean["manufacturer_name_upper"] = canonical_upper(hierarchy.get("manufacturer_name"))
    clean["model_name"] = hierarchy.get("model_name")
    clean["model_name_upper"] = canonical_upper(hierarchy.get("model_name"))
    clean["generation_name"] = hierarchy.get("generation_name")
    clean["generation_name_canonical"] = hierarchy.get("generation_name_canonical")
    clean["generation_name_upper"] = canonical_upper(hierarchy.get("generation_name"))
    clean["version_name"] = hierarchy.get("version_name")
    clean["version_name_canonical"] = hierarchy.get("version_name_canonical")
    clean["version_name_upper"] = canonical_upper(hierarchy.get("version_name"))

    for key, value in production.items():
        clean[key] = value

    map_summary_data(clean, summary)
    map_section_data(clean, sections)
    enrich_derived_fields(clean, sections, summary)
    build_ids(clean)
    ok, missing = minimum_required_ok(clean, contract)

    raw = {
        "source": "encycarpedia",
        "source_version_url": clean["source_version_url"],
        "canonical_url": meta.get("canonical"),
        "html_lang": clean.get("html_lang"),
        "scrape_timestamp_utc": clean["scrape_timestamp"],
        "scraper_version": SCRAPER_VERSION,
        "parser_version": PARSER_VERSION,
        "capture_mode": "html",
        "headline": hierarchy.get("headline"),
        "meta": meta,
        "breadcrumbs": breadcrumbs,
        "summary": summary,
        "sections": sections,
        "section_names": list(sections.keys()),
        "jsonld_date_modified": jsonld.get("dateModified") if isinstance(jsonld, dict) else None,
        "quality_flags": {
            "minimum_required_ok": ok,
            "missing_minimum_fields": missing,
            "summary_fields_detected": len(summary),
            "sections_detected": len(sections),
        },
    }
    return raw, clean


def parse_html_file(path: str | Path, contract: dict[str, Any], source_url: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    html = Path(path).read_text(encoding="utf-8", errors="ignore")
    return parse_version_html(html=html, source_url=source_url, contract=contract)


parse_html_to_dicts = parse_version_html
