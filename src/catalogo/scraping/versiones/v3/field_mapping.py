from __future__ import annotations

import re
from typing import Any

# -----------------------------------------------------------------------------
# Constantes consumidas por parser.py
# -----------------------------------------------------------------------------

SUMMARY_FIELD_MAP: dict[str, str] = {
    "Gasolina Motor": "engine_name",
    "Diésel Motor": "engine_name",
    "Velocidad Máxima": "top_speed_kmh",
    "0-100 Km/h Aceleración": "acceleration_0_100_s",
    "Potencia Total": "power_cv",
    "Consumos (Medio)": "fuel_consumption_combined_l_100km",
    "Puertas": "doors",
    "Asientos": "seats",
    "Capacitad Maletero": "boot_capacity_l",
    "Capacidad Maletero": "boot_capacity_l",
    "Peso en Vacío": "kerb_weight_kg",
    "Disposición del Tren Motriz": "drive_type_label",
}

SECTION_FIELD_MAP: dict[str, dict[str, str]] = {
    "Datos de Prestaciones": {
        "Velocidad Máxima": "top_speed_kmh",
        "0-100 Km/h": "acceleration_0_100_s",
        "Potencia": "max_power_cv",
        "Par": "max_torque_nm",
        "Relación Potencia-Peso": "power_to_weight_cv_ton",
    },
    "Economía de Combustible": {
        "Medio": "fuel_consumption_combined_l_100km",
        "Urbano": "fuel_consumption_urban_l_100km",
        "Extraurbano": "fuel_consumption_extraurban_l_100km",
        "Autonomía Total": "range_km",
    },
    "Gasolina Motor": {
        "Cilindrada": "engine_displacement_cc",
        "Configuración": "engine_layout",
        "Inducción": "aspiration",
        "Potencia Máximo": "max_power_cv",
        "Par Máximo": "max_torque_nm",
        "Tren de Válvulas": "valvetrain",
        "Válvulas/Cilindro": "valves_per_cylinder",
        "Alimentación": "fuel_system",
        "Posición": "engine_position",
        "Orientación": "engine_orientation",
        "Combustible": "fuel_type",
        "Capacitad Depósito": "fuel_tank_l",
        "Capacidad Depósito": "fuel_tank_l",
    },
    "Diésel Motor": {
        "Cilindrada": "engine_displacement_cc",
        "Configuración": "engine_layout",
        "Inducción": "aspiration",
        "Potencia Máximo": "max_power_cv",
        "Par Máximo": "max_torque_nm",
        "Tren de Válvulas": "valvetrain",
        "Válvulas/Cilindro": "valves_per_cylinder",
        "Alimentación": "fuel_system",
        "Posición": "engine_position",
        "Orientación": "engine_orientation",
        "Combustible": "fuel_type",
        "Capacitad Depósito": "fuel_tank_l",
        "Capacidad Depósito": "fuel_tank_l",
    },
    "Más Datos del Motor": {
        "Índice de Compresión": "compression_ratio",
        "Diámetro x Carrera": "bore_stroke_text",
        "Relación Diámetro-Carrera": "bore_stroke_ratio",
        "Salida Específica": "specific_output_cv_l",
        "Potencia/Cilindro": "power_per_cylinder_cv",
        "Cilindrada Unitaria": "unitary_displacement_cc",
        "PME": "bmep_bar",
    },
    "Tren Motriz y Chasis": {
        "Ruedas Motrices": "drive_type",
        "Caja De Cambios (MT)": "gearbox_label",
        "Caja de Cambios (MT)": "gearbox_label",
        "Neumáticos": "tyre_size",
        "Suspensión Delantera": "front_suspension",
        "Suspensión Trasera": "rear_suspension",
        "Frenos Delanteros": "front_brakes",
        "Frenos Traseros": "rear_brakes",
    },
    "Dimensiones y Practicidad": {
        "Carrocería": "body_type",
        "Puertas": "doors",
        "Asientos": "seats",
        "Capacitad Maletero": "boot_capacity_l",
        "Capacidad Maletero": "boot_capacity_l",
        "Peso en Vacío": "kerb_weight_kg",
        "Peso Bruto": "gross_weight_kg",
        "Capacidad de Carga": "payload_kg",
        "Capacidad de Remolque": "towing_capacity_braked_kg",
        "Longitud": "length_mm",
        "Anchura": "width_mm",
        "Altura": "height_mm",
        "Batalla": "wheelbase_mm",
        "Via Delantera": "front_track_mm",
        "Vía Delantera": "front_track_mm",
        "Via Trasera": "rear_track_mm",
        "Vía Trasera": "rear_track_mm",
    },
    "Resultados de Euro NCAP": {
        "Euro NCAP": "euro_ncap",
    },
}


# -----------------------------------------------------------------------------
# Helpers básicos
# -----------------------------------------------------------------------------

def _slugify(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip().lower()
    if not text:
        return None
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_-]+", "-", text, flags=re.UNICODE)
    text = re.sub(r"^-+|-+$", "", text)
    return text or None


def _upper(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value.upper() if value else None


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _first_number_str(text: Any) -> str | None:
    if text is None:
        return None
    s = str(text).strip().replace(",", ".")
    match = re.search(r"-?\d+(?:\.\d+)?", s)
    if not match:
        return None
    return match.group(0)


def _first_number(text: Any) -> float | None:
    n = _first_number_str(text)
    if n is None:
        return None
    try:
        return float(n)
    except Exception:
        return None


def _to_int(text: Any) -> int | None:
    n = _first_number(text)
    return int(round(n)) if n is not None else None


def _to_float(text: Any) -> float | None:
    return _first_number(text)

def _to_kg_int(text: Any) -> int | None:
    if text is None:
        return None
    s = str(text).strip()
    if not s:
        return None

    digits = re.sub(r"[^\d]", "", s)
    if not digits:
        return None

    try:
        return int(digits)
    except Exception:
        return None

def _to_mm_int(text: Any) -> int | None:
    if text is None:
        return None
    s = str(text).strip()
    if not s:
        return None

    lower = s.lower()
    if "mm" in lower:
        digits = re.sub(r"[^\d]", "", s)
        if digits:
            try:
                return int(digits)
            except Exception:
                return None

    n = _first_number(s)
    if n is None:
        return None

    # Si viene como 3.638 y el texto original parece una medida europea con separador de miles,
    # lo tratamos como 3638 mm.
    if "." in s and "mm" in lower and n < 20:
        digits = re.sub(r"[^\d]", "", s)
        if digits:
            try:
                return int(digits)
            except Exception:
                pass

    # Fallback conservador
    if n < 20:
        return int(round(n * 1000))
    return int(round(n))


def _extract_cc_from_text(text: Any) -> int | None:
    if text is None:
        return None
    s = str(text).strip().lower()
    if not s:
        return None

    # Si aparece explícitamente cc, preferir ese número
    if "cc" in s:
        digits = re.sub(r"[^\d]", "", s)
        if digits:
            try:
                return int(digits)
            except Exception:
                return None

    # Si viene como 1,5 Litro o 1.5 Litro
    n = _first_number(s)
    if n is None:
        return None
    if "litro" in s or "l" in s:
        return int(round(n * 1000))
    return int(round(n))


def _extract_years(text: str | None) -> tuple[int | None, int | None]:
    if not text:
        return None, None
    years = re.findall(r"\b(?:19|20)\d{2}\b", text)
    if not years:
        return None, None
    start = int(years[0])
    end = int(years[-1])
    return start, end


def _get_meta(raw_dict: dict[str, Any], key: str) -> Any:
    meta = raw_dict.get("meta") or {}
    if isinstance(meta, dict):
        return meta.get(key)
    return None


def _get_breadcrumbs(raw_dict: dict[str, Any]) -> list[dict[str, Any]]:
    breadcrumbs = raw_dict.get("breadcrumbs")
    return breadcrumbs if isinstance(breadcrumbs, list) else []


def _breadcrumb_name(raw_dict: dict[str, Any], position: int) -> str | None:
    for crumb in _get_breadcrumbs(raw_dict):
        if crumb.get("position") == position:
            return _clean_text(crumb.get("name"))
    return None


def _breadcrumb_item(raw_dict: dict[str, Any], position: int) -> str | None:
    for crumb in _get_breadcrumbs(raw_dict):
        if crumb.get("position") == position:
            return _clean_text(crumb.get("item"))
    return None


def _get_summary(raw_dict: dict[str, Any], key: str) -> Any:
    summary = raw_dict.get("summary") or {}
    if isinstance(summary, dict):
        return summary.get(key)
    return None


def _get_section_value(raw_dict: dict[str, Any], section_name: str, key: str) -> Any:
    sections = raw_dict.get("sections") or {}
    if not isinstance(sections, dict):
        return None
    section = sections.get(section_name) or {}
    if not isinstance(section, dict):
        return None
    return section.get(key)


def _coalesce(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _first_item(value: Any) -> Any:
    if isinstance(value, list) and value:
        return value[0]
    return value


def _second_item(value: Any) -> Any:
    if isinstance(value, list) and len(value) > 1:
        return value[1]
    return None


def _extract_from_breadcrumbs(raw_dict: dict[str, Any]) -> tuple[str | None, str | None, str | None, str | None]:
    manufacturer_name = _breadcrumb_name(raw_dict, 1)
    generation_name = _breadcrumb_name(raw_dict, 2)
    breadcrumb_3 = _breadcrumb_name(raw_dict, 3)

    model_name = None
    if generation_name:
        model_name = re.sub(r"\s*\((?:19|20)\d{2}.*?\)\s*$", "", generation_name).strip() or generation_name

    version_name = None
    if breadcrumb_3:
        text = breadcrumb_3
        text = re.sub(r"^\s*(?:19|20)\d{2}\s+", "", text)
        if manufacturer_name:
            text = re.sub(rf"^\s*{re.escape(manufacturer_name)}\s+", "", text, flags=re.IGNORECASE)
        if model_name:
            text = re.sub(rf"^\s*{re.escape(model_name)}\s+", "", text, flags=re.IGNORECASE)
        version_name = text.strip(" -") or None

    return manufacturer_name, model_name, generation_name, version_name


def _extract_from_headline(raw_dict: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    headline = _clean_text(raw_dict.get("headline"))
    if not headline:
        return None, None, None

    main = headline.split(" - ")[0].strip()
    match = re.match(r"^(?P<year>(?:19|20)\d{2})\s+(?P<make>\S+)\s+(?P<model>\S+)\s+(?P<version>.+)$", main)
    if not match:
        return None, None, None

    manufacturer_name = match.group("make").strip()
    model_name = match.group("model").strip()
    version_name = match.group("version").strip()
    return manufacturer_name, model_name, version_name


def _normalize_drive_type(value: Any) -> tuple[str | None, str | None]:
    first = _clean_text(_first_item(value))
    second = _clean_text(_second_item(value))
    text = _coalesce(first, second)
    if not text:
        return None, None

    upper = text.upper()
    if "FWD" in upper or "DELANTERA" in upper:
        return "FWD", "Tracción Delantera"
    if "RWD" in upper or "TRASERA" in upper:
        return "RWD", "Tracción Trasera"
    if "AWD" in upper or "4WD" in upper:
        return "AWD", text
    return text, text


def _parse_doors(value: Any) -> int | None:
    text = _clean_text(value)
    if not text:
        return None
    nums = re.findall(r"\d+", text)
    if not nums:
        return None
    try:
        return int(nums[-1])
    except Exception:
        return None


def _parse_seats(value: Any) -> int | None:
    return _to_int(value)


def _parse_engine_displacement_cc(value: Any) -> int | None:
    first = _first_item(value)
    second = _second_item(value)
    return _extract_cc_from_text(_coalesce(second, first))


def _parse_engine_displacement_l(value: Any) -> float | None:
    first = _first_item(value)
    return _to_float(first)


def _parse_power_cv(value: Any) -> int | None:
    return _to_int(_first_item(value))


def _parse_power_bhp(value: Any) -> int | None:
    return _to_int(_second_item(value))


def _parse_torque_nm(value: Any) -> float | None:
    return _to_float(_first_item(value))


def _parse_torque_lbft(value: Any) -> float | None:
    return _to_float(_second_item(value))


def _parse_rpm(value: Any) -> int | None:
    text = _clean_text(_first_item(value))
    if not text:
        return None
    match = re.search(r"@\s*([\d\.\,]+)", text)
    if not match:
        return None
    raw = match.group(1).replace(".", "").replace(",", "")
    try:
        return int(raw)
    except Exception:
        return None


def _parse_valves_per_cylinder(value: Any) -> int | None:
    text = _clean_text(value)
    if not text:
        return None
    match = re.search(r"(\d+)\s*\(", text)
    if match:
        return int(match.group(1))
    return _to_int(text)


def _parse_valves_total(value: Any) -> int | None:
    text = _clean_text(value)
    if not text:
        return None
    match = re.search(r"(\d+)v", text, flags=re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _parse_bore_stroke(value: Any) -> tuple[float | None, float | None, str | None]:
    text = _clean_text(value)
    if not text:
        return None, None, None
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*x\s*(\d+(?:[.,]\d+)?)", text, flags=re.IGNORECASE)
    if not match:
        return None, None, text
    bore = float(match.group(1).replace(",", "."))
    stroke = float(match.group(2).replace(",", "."))
    return bore, stroke, text


def _parse_ratio_and_label(value: Any) -> tuple[float | None, str | None]:
    first = _clean_text(_first_item(value))
    second = _clean_text(_second_item(value))
    ratio = _to_float(first)
    return ratio, second


def _parse_bmep(value: Any) -> tuple[float | None, float | None]:
    first = _first_item(value)
    second = _second_item(value)
    return _to_float(first), _to_float(second)


def _parse_gearbox_label_and_count(value: Any) -> tuple[str | None, int | None]:
    text = _clean_text(value)
    if not text:
        return None, None
    return text, _to_int(text)


def _parse_towing_capacity(value: Any) -> tuple[float | None, float | None]:
    text = _clean_text(value)
    if not text:
        return None, None
    nums = re.findall(r"\d+(?:[.,]\d+)?", text)
    if not nums:
        return None, None
    if len(nums) == 1:
        v = float(nums[0].replace(",", "."))
        return v, None
    first = float(nums[0].replace(",", "."))
    second = float(nums[1].replace(",", "."))
    return second, first


# -----------------------------------------------------------------------------
# Mapping principal
# -----------------------------------------------------------------------------

def map_raw_to_clean(raw_dict: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    fields = contract.get("fields", {})
    clean: dict[str, Any] = {field_name: None for field_name in fields.keys()}

    bc_make, bc_model, bc_generation, bc_version = _extract_from_breadcrumbs(raw_dict)
    hl_make, hl_model, hl_version = _extract_from_headline(raw_dict)

    manufacturer_name = _coalesce(raw_dict.get("manufacturer_name"), bc_make, hl_make)
    model_name = _coalesce(raw_dict.get("model_name"), bc_model, hl_model)
    generation_name = _coalesce(raw_dict.get("generation_name"), bc_generation)
    version_name = _coalesce(raw_dict.get("version_name"), bc_version, hl_version)

    source = _coalesce(raw_dict.get("source"), "encycarpedia")
    source_version_url = _coalesce(raw_dict.get("source_version_url"), raw_dict.get("source_url"))
    canonical_url = _coalesce(raw_dict.get("canonical_url"), _get_meta(raw_dict, "canonical"), source_version_url)

    headline = _coalesce(raw_dict.get("headline"), _get_meta(raw_dict, "og_title"))
    meta_description = _coalesce(
        raw_dict.get("meta_description"),
        _get_meta(raw_dict, "meta_description"),
        _get_meta(raw_dict, "og_description"),
    )

    drive_type_raw = _coalesce(
        _get_section_value(raw_dict, "Tren Motriz y Chasis", "Ruedas Motrices"),
        _get_summary(raw_dict, "Disposición del Tren Motriz"),
    )
    drive_type, drive_type_label = _normalize_drive_type(drive_type_raw)

    power_max = _coalesce(
        _get_section_value(raw_dict, "Gasolina Motor", "Potencia Máximo"),
        _get_section_value(raw_dict, "Diésel Motor", "Potencia Máximo"),
    )
    torque_max = _coalesce(
        _get_section_value(raw_dict, "Gasolina Motor", "Par Máximo"),
        _get_section_value(raw_dict, "Diésel Motor", "Par Máximo"),
    )
    displacement = _coalesce(
        _get_section_value(raw_dict, "Gasolina Motor", "Cilindrada"),
        _get_section_value(raw_dict, "Diésel Motor", "Cilindrada"),
    )
    fuel_type = _coalesce(
        _get_section_value(raw_dict, "Gasolina Motor", "Combustible"),
        _get_section_value(raw_dict, "Diésel Motor", "Combustible"),
    )
    engine_layout = _coalesce(
        _get_section_value(raw_dict, "Gasolina Motor", "Configuración"),
        _get_section_value(raw_dict, "Diésel Motor", "Configuración"),
    )
    aspiration = _coalesce(
        _get_section_value(raw_dict, "Gasolina Motor", "Inducción"),
        _get_section_value(raw_dict, "Diésel Motor", "Inducción"),
    )
    fuel_system = _coalesce(
        _get_section_value(raw_dict, "Gasolina Motor", "Alimentación"),
        _get_section_value(raw_dict, "Diésel Motor", "Alimentación"),
    )
    valvetrain = _coalesce(
        _get_section_value(raw_dict, "Gasolina Motor", "Tren de Válvulas"),
        _get_section_value(raw_dict, "Diésel Motor", "Tren de Válvulas"),
    )
    valves_pc_raw = _coalesce(
        _get_section_value(raw_dict, "Gasolina Motor", "Válvulas/Cilindro"),
        _get_section_value(raw_dict, "Diésel Motor", "Válvulas/Cilindro"),
    )
    engine_position = _coalesce(
        _get_section_value(raw_dict, "Gasolina Motor", "Posición"),
        _get_section_value(raw_dict, "Diésel Motor", "Posición"),
    )
    engine_orientation = _coalesce(
        _get_section_value(raw_dict, "Gasolina Motor", "Orientación"),
        _get_section_value(raw_dict, "Diésel Motor", "Orientación"),
    )
    fuel_tank_raw = _coalesce(
        _get_section_value(raw_dict, "Gasolina Motor", "Capacitad Depósito"),
        _get_section_value(raw_dict, "Gasolina Motor", "Capacidad Depósito"),
        _get_section_value(raw_dict, "Diésel Motor", "Capacitad Depósito"),
        _get_section_value(raw_dict, "Diésel Motor", "Capacidad Depósito"),
    )

    bore, stroke, bore_stroke_text = _parse_bore_stroke(
        _get_section_value(raw_dict, "Más Datos del Motor", "Diámetro x Carrera")
    )
    bore_stroke_ratio, bore_stroke_ratio_label = _parse_ratio_and_label(
        _get_section_value(raw_dict, "Más Datos del Motor", "Relación Diámetro-Carrera")
    )
    bmep_bar, bmep_psi = _parse_bmep(
        _get_section_value(raw_dict, "Más Datos del Motor", "PME")
    )

    years_text = meta_description or headline
    production_start_year, production_end_year = _extract_years(years_text)

    body_type = _clean_text(_get_section_value(raw_dict, "Dimensiones y Practicidad", "Carrocería"))

    doors = _parse_doors(
        _coalesce(
            _get_section_value(raw_dict, "Dimensiones y Practicidad", "Puertas"),
            _get_summary(raw_dict, "Puertas"),
        )
    )
    seats = _parse_seats(
        _coalesce(
            _get_section_value(raw_dict, "Dimensiones y Practicidad", "Asientos"),
            _get_summary(raw_dict, "Asientos"),
        )
    )

    boot_capacity_l = _to_float(
        _coalesce(
            _get_section_value(raw_dict, "Dimensiones y Practicidad", "Capacitad Maletero"),
            _get_section_value(raw_dict, "Dimensiones y Practicidad", "Capacidad Maletero"),
            _get_summary(raw_dict, "Capacitad Maletero"),
            _get_summary(raw_dict, "Capacidad Maletero"),
        )
    )

    gearbox_label, gear_count = _parse_gearbox_label_and_count(
        _coalesce(
            _get_section_value(raw_dict, "Tren Motriz y Chasis", "Caja De Cambios (MT)"),
            _get_section_value(raw_dict, "Tren Motriz y Chasis", "Caja de Cambios (MT)"),
        )
    )

    towing_braked, towing_unbraked = _parse_towing_capacity(
        _get_section_value(raw_dict, "Dimensiones y Practicidad", "Capacidad de Remolque")
    )

    kerb = _coalesce(
        _get_section_value(raw_dict, "Dimensiones y Practicidad", "Peso en Vacío"),
        _get_summary(raw_dict, "Peso en Vacío"),
    )
    if isinstance(kerb, str) and "indisponible" in kerb.lower():
        kerb = None

    clean["source"] = source
    clean["source_version_url"] = source_version_url
    clean["source_version_url_canonical"] = canonical_url
    clean["source_generation_url"] = _breadcrumb_item(raw_dict, 2)
    clean["source_model_url"] = None
    clean["source_manufacturer_url"] = _breadcrumb_item(raw_dict, 1)

    clean["scrape_date"] = None
    clean["scrape_timestamp"] = _coalesce(raw_dict.get("scrape_timestamp"), raw_dict.get("scrape_timestamp_utc"))
    clean["html_lang"] = _coalesce(raw_dict.get("html_lang"), _get_meta(raw_dict, "html_lang"))
    clean["source_date_modified"] = raw_dict.get("jsonld_date_modified")

    clean["manufacturer_name"] = manufacturer_name
    clean["manufacturer_name_upper"] = _upper(manufacturer_name)

    clean["model_name"] = model_name
    clean["model_name_upper"] = _upper(model_name)

    clean["generation_name"] = generation_name
    clean["generation_name_canonical"] = generation_name
    clean["generation_name_upper"] = _upper(generation_name)

    clean["version_name"] = version_name
    clean["version_name_canonical"] = version_name
    clean["version_name_upper"] = _upper(version_name)

    clean["full_title"] = _coalesce(_get_meta(raw_dict, "og_title"), headline)
    clean["headline"] = headline
    clean["meta_description"] = meta_description

    clean["body_type"] = body_type
    clean["trim"] = None
    clean["facelift_status"] = "preactualizado" if meta_description and "preactualizado" in meta_description.lower() else None
    clean["doors"] = doors
    clean["seats"] = seats

    clean["production_start_year"] = production_start_year
    clean["production_end_year"] = production_end_year
    clean["production_years_text"] = f"{production_start_year}-{production_end_year}" if production_start_year and production_end_year else None
    clean["model_year"] = _to_int(headline)
    clean["is_current_generation"] = None

    clean["power_cv"] = _to_int(
        _coalesce(
            _get_summary(raw_dict, "Potencia Total"),
            _get_section_value(raw_dict, "Datos de Prestaciones", "Potencia"),
        )
    )
    clean["power_bhp"] = _parse_power_bhp(power_max)
    clean["fuel_type"] = fuel_type
    clean["drive_type"] = drive_type
    clean["drive_type_label"] = drive_type_label

    clean["engine_name"] = _coalesce(_get_summary(raw_dict, "Gasolina Motor"), _get_summary(raw_dict, "Diésel Motor"))
    clean["engine_code"] = None
    clean["engine_family"] = None
    clean["engine_type"] = fuel_type
    clean["engine_layout"] = engine_layout
    clean["cylinders"] = _to_int(engine_layout)
    clean["valves_total"] = _parse_valves_total(valves_pc_raw)
    clean["valves_per_cylinder"] = _parse_valves_per_cylinder(valves_pc_raw)
    clean["valvetrain"] = valvetrain
    clean["aspiration"] = aspiration
    clean["fuel_system"] = fuel_system
    clean["engine_position"] = engine_position
    clean["engine_orientation"] = engine_orientation

    clean["engine_displacement_cc"] = _parse_engine_displacement_cc(displacement)
    clean["engine_displacement_l"] = _parse_engine_displacement_l(displacement)
    clean["unitary_displacement_cc"] = _to_float(_get_section_value(raw_dict, "Más Datos del Motor", "Cilindrada Unitaria"))
    clean["compression_ratio"] = _to_float(_get_section_value(raw_dict, "Más Datos del Motor", "Índice de Compresión"))
    clean["bore_mm"] = bore
    clean["stroke_mm"] = stroke
    clean["bore_stroke_text"] = bore_stroke_text
    clean["bore_stroke_ratio"] = bore_stroke_ratio
    clean["bore_stroke_ratio_label"] = bore_stroke_ratio_label

    clean["max_power_cv"] = _parse_power_cv(power_max)
    clean["max_power_kw"] = None
    clean["max_power_bhp"] = _parse_power_bhp(power_max)
    clean["max_power_rpm"] = _parse_rpm(power_max)

    clean["max_torque_nm"] = _parse_torque_nm(torque_max)
    clean["max_torque_lbft"] = _parse_torque_lbft(torque_max)
    clean["max_torque_rpm"] = _parse_rpm(torque_max)

    clean["specific_output_cv_l"] = _to_float(_get_section_value(raw_dict, "Más Datos del Motor", "Salida Específica"))
    clean["specific_output_kw_l"] = None
    clean["power_per_cylinder_cv"] = _to_float(_get_section_value(raw_dict, "Más Datos del Motor", "Potencia/Cilindro"))
    clean["bmep_bar"] = bmep_bar
    clean["bmep_psi"] = bmep_psi

    clean["top_speed_kmh"] = _to_float(
        _coalesce(
            _get_summary(raw_dict, "Velocidad Máxima"),
            _get_section_value(raw_dict, "Datos de Prestaciones", "Velocidad Máxima"),
        )
    )
    clean["top_speed_mph"] = None
    clean["acceleration_0_100_s"] = _to_float(
        _coalesce(
            _get_summary(raw_dict, "0-100 Km/h Aceleración"),
            _get_section_value(raw_dict, "Datos de Prestaciones", "0-100 Km/h"),
        )
    )
    clean["acceleration_0_62_s"] = None
    clean["power_to_weight_cv_ton"] = None
    clean["power_to_weight_kw_ton"] = None

    clean["fuel_consumption_urban_l_100km"] = None
    clean["fuel_consumption_extraurban_l_100km"] = None
    clean["fuel_consumption_combined_l_100km"] = _to_float(
        _coalesce(
            _get_summary(raw_dict, "Consumos (Medio)"),
            _get_section_value(raw_dict, "Economía de Combustible", "Medio"),
        )
    )
    clean["fuel_consumption_combined_mpg_uk"] = None
    clean["fuel_consumption_combined_mpg_us"] = None

    clean["co2_emissions_g_km"] = None
    clean["emission_standard"] = None
    clean["start_stop"] = None
    clean["euro_ncap"] = _clean_text(_get_section_value(raw_dict, "Resultados de Euro NCAP", "Euro NCAP"))

    clean["gearbox_type"] = None
    clean["gearbox_label"] = gearbox_label
    clean["gear_count"] = gear_count
    clean["clutch_type"] = None

    clean["front_suspension"] = _clean_text(_get_section_value(raw_dict, "Tren Motriz y Chasis", "Suspensión Delantera"))
    clean["rear_suspension"] = _clean_text(_get_section_value(raw_dict, "Tren Motriz y Chasis", "Suspensión Trasera"))
    clean["front_brakes"] = _clean_text(_get_section_value(raw_dict, "Tren Motriz y Chasis", "Frenos Delanteros"))
    clean["rear_brakes"] = _clean_text(_get_section_value(raw_dict, "Tren Motriz y Chasis", "Frenos Traseros"))
    clean["steering_type"] = None
    clean["turning_circle_m"] = None

    clean["tyre_size"] = _clean_text(_get_section_value(raw_dict, "Tren Motriz y Chasis", "Neumáticos"))
    clean["front_tyre_size"] = None
    clean["rear_tyre_size"] = None
    clean["wheel_size"] = None
    clean["front_wheel_size"] = None
    clean["rear_wheel_size"] = None

    clean["length_mm"] = _to_mm_int(_get_section_value(raw_dict, "Dimensiones y Practicidad", "Longitud"))
    clean["width_mm"] = _to_mm_int(_get_section_value(raw_dict, "Dimensiones y Practicidad", "Anchura"))
    clean["width_including_mirrors_mm"] = None
    clean["height_mm"] = _to_mm_int(_get_section_value(raw_dict, "Dimensiones y Practicidad", "Altura"))
    clean["wheelbase_mm"] = _to_mm_int(_get_section_value(raw_dict, "Dimensiones y Practicidad", "Batalla"))
    clean["front_track_mm"] = _to_mm_int(
        _coalesce(
            _get_section_value(raw_dict, "Dimensiones y Practicidad", "Via Delantera"),
            _get_section_value(raw_dict, "Dimensiones y Practicidad", "Vía Delantera"),
        )
    )
    clean["rear_track_mm"] = _to_mm_int(
        _coalesce(
            _get_section_value(raw_dict, "Dimensiones y Practicidad", "Via Trasera"),
            _get_section_value(raw_dict, "Dimensiones y Practicidad", "Vía Trasera"),
        )
    )
    clean["ground_clearance_mm"] = None

    clean["kerb_weight_kg"] = _to_kg_int(kerb)
    clean["gross_weight_kg"] = _to_kg_int(_get_section_value(raw_dict, "Dimensiones y Practicidad", "Peso Bruto"))
    clean["payload_kg"] = _to_kg_int(_get_section_value(raw_dict, "Dimensiones y Practicidad", "Capacidad de Carga"))
    clean["towing_capacity_braked_kg"] = _to_kg_int(_get_section_value(raw_dict, "Dimensiones y Practicidad", "Capacidad de Remolque"))
    clean["towing_capacity_unbraked_kg"] = None

    clean["boot_capacity_l"] = boot_capacity_l
    clean["boot_capacity_min_l"] = None
    clean["boot_capacity_max_l"] = None
    clean["fuel_tank_l"] = _to_float(fuel_tank_raw)

    manufacturer_slug = _slugify(manufacturer_name) or "unknown-manufacturer"
    model_slug = _slugify(model_name) or "unknown-model"
    generation_slug = _slugify(generation_name) or "unknown-generation"
    version_slug = _slugify(version_name) or "unknown-version"

    clean["manufacturer_id"] = raw_dict.get("manufacturer_id") or manufacturer_slug
    clean["model_id"] = raw_dict.get("model_id") or f"{manufacturer_slug}__{model_slug}"
    clean["generation_id"] = raw_dict.get("generation_id") or f"{manufacturer_slug}__{model_slug}__{generation_slug}"
    clean["version_id"] = raw_dict.get("version_id") or f"{manufacturer_slug}__{model_slug}__{generation_slug}__{version_slug}"

    return clean