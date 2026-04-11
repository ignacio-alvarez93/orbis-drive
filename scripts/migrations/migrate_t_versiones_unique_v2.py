from __future__ import annotations

import argparse
import shutil
import sqlite3
from pathlib import Path


CREATE_T_VERSIONES_NEW = """
CREATE TABLE T_Versiones_new (
    version_id TEXT PRIMARY KEY,

    manufacturer_id TEXT NOT NULL,
    model_id TEXT NOT NULL,
    generation_id TEXT NOT NULL,

    source TEXT,
    source_version_url TEXT,
    source_version_url_canonical TEXT,
    source_generation_url TEXT,
    source_model_url TEXT,
    source_manufacturer_url TEXT,

    scrape_date TEXT,
    scrape_timestamp TEXT,
    html_lang TEXT,
    source_date_modified TEXT,

    manufacturer_name TEXT,
    manufacturer_name_upper TEXT,

    model_name TEXT,
    model_name_upper TEXT,

    generation_name TEXT,
    generation_name_canonical TEXT,
    generation_name_upper TEXT,

    version_name TEXT,
    version_name_canonical TEXT,
    version_name_upper TEXT,

    full_title TEXT,
    headline TEXT,
    meta_description TEXT,

    body_type TEXT,
    trim TEXT,
    facelift_status TEXT,
    doors INTEGER,
    seats INTEGER,

    production_start_year INTEGER,
    production_end_year INTEGER,
    production_years_text TEXT,
    model_year INTEGER,
    is_current_generation INTEGER,

    power_cv REAL,
    power_bhp REAL,
    fuel_type TEXT,
    drive_type TEXT,
    drive_type_label TEXT,

    engine_name TEXT,
    engine_code TEXT,
    engine_family TEXT,
    engine_type TEXT,
    engine_layout TEXT,
    cylinders INTEGER,
    valves_total INTEGER,
    valves_per_cylinder INTEGER,
    valvetrain TEXT,
    aspiration TEXT,
    fuel_system TEXT,
    engine_position TEXT,
    engine_orientation TEXT,

    engine_displacement_cc REAL,
    engine_displacement_l REAL,
    unitary_displacement_cc REAL,
    compression_ratio REAL,
    bore_mm REAL,
    stroke_mm REAL,
    bore_stroke_text TEXT,
    bore_stroke_ratio REAL,
    bore_stroke_ratio_label TEXT,

    max_power_cv REAL,
    max_power_kw REAL,
    max_power_bhp REAL,
    max_power_rpm REAL,

    max_torque_nm REAL,
    max_torque_lbft REAL,
    max_torque_rpm REAL,

    specific_output_cv_l REAL,
    specific_output_kw_l REAL,
    power_per_cylinder_cv REAL,
    bmep_bar REAL,
    bmep_psi REAL,

    top_speed_kmh REAL,
    top_speed_mph REAL,
    acceleration_0_100_s REAL,
    acceleration_0_62_s REAL,
    power_to_weight_cv_ton REAL,
    power_to_weight_kw_ton REAL,

    fuel_consumption_urban_l_100km REAL,
    fuel_consumption_extraurban_l_100km REAL,
    fuel_consumption_combined_l_100km REAL,
    fuel_consumption_combined_mpg_uk REAL,
    fuel_consumption_combined_mpg_us REAL,

    co2_emissions_g_km REAL,
    emission_standard TEXT,
    start_stop INTEGER,
    euro_ncap TEXT,

    gearbox_type TEXT,
    gearbox_label TEXT,
    gear_count INTEGER,
    clutch_type TEXT,

    front_suspension TEXT,
    rear_suspension TEXT,
    front_brakes TEXT,
    rear_brakes TEXT,
    steering_type TEXT,
    turning_circle_m REAL,

    tyre_size TEXT,
    front_tyre_size TEXT,
    rear_tyre_size TEXT,
    wheel_size TEXT,
    front_wheel_size TEXT,
    rear_wheel_size TEXT,

    length_mm REAL,
    width_mm REAL,
    width_including_mirrors_mm REAL,
    height_mm REAL,
    wheelbase_mm REAL,
    front_track_mm REAL,
    rear_track_mm REAL,
    ground_clearance_mm REAL,

    kerb_weight_kg REAL,
    gross_weight_kg REAL,
    payload_kg REAL,
    towing_capacity_braked_kg REAL,
    towing_capacity_unbraked_kg REAL,

    boot_capacity_l REAL,
    boot_capacity_min_l REAL,
    boot_capacity_max_l REAL,
    fuel_tank_l REAL,

    match_key_manufacturer TEXT,
    match_key_model TEXT,
    match_key_generation TEXT,
    match_key_version TEXT,

    is_complete_minimum INTEGER,
    has_engine_block INTEGER,
    has_drivetrain_block INTEGER,
    has_dimensions_block INTEGER,
    has_performance_block INTEGER,
    has_weights_block INTEGER,

    FOREIGN KEY (manufacturer_id) REFERENCES T_Fabricantes(manufacturer_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (model_id) REFERENCES T_Modelos(model_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (generation_id) REFERENCES T_Generaciones(generation_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    UNIQUE (
        version_name_canonical,
        generation_id,
        production_start_year,
        production_end_year
    )
);
"""

RECREATE_INDEXES = [
    "CREATE INDEX idx_versiones_drive_type ON T_Versiones(drive_type);",
    "CREATE INDEX idx_versiones_fuel_type ON T_Versiones(fuel_type);",
    "CREATE INDEX idx_versiones_generation_id ON T_Versiones(generation_id);",
    "CREATE INDEX idx_versiones_manufacturer_id ON T_Versiones(manufacturer_id);",
    "CREATE INDEX idx_versiones_model_id ON T_Versiones(model_id);",
    "CREATE INDEX idx_versiones_power_cv ON T_Versiones(power_cv);",
    "CREATE INDEX idx_versiones_version_name_canonical ON T_Versiones(version_name_canonical);",
]

ALL_COLUMNS = [
    "version_id", "manufacturer_id", "model_id", "generation_id",
    "source", "source_version_url", "source_version_url_canonical", "source_generation_url",
    "source_model_url", "source_manufacturer_url", "scrape_date", "scrape_timestamp",
    "html_lang", "source_date_modified", "manufacturer_name", "manufacturer_name_upper",
    "model_name", "model_name_upper", "generation_name", "generation_name_canonical",
    "generation_name_upper", "version_name", "version_name_canonical", "version_name_upper",
    "full_title", "headline", "meta_description", "body_type", "trim", "facelift_status",
    "doors", "seats", "production_start_year", "production_end_year", "production_years_text",
    "model_year", "is_current_generation", "power_cv", "power_bhp", "fuel_type", "drive_type",
    "drive_type_label", "engine_name", "engine_code", "engine_family", "engine_type",
    "engine_layout", "cylinders", "valves_total", "valves_per_cylinder", "valvetrain",
    "aspiration", "fuel_system", "engine_position", "engine_orientation",
    "engine_displacement_cc", "engine_displacement_l", "unitary_displacement_cc",
    "compression_ratio", "bore_mm", "stroke_mm", "bore_stroke_text", "bore_stroke_ratio",
    "bore_stroke_ratio_label", "max_power_cv", "max_power_kw", "max_power_bhp",
    "max_power_rpm", "max_torque_nm", "max_torque_lbft", "max_torque_rpm",
    "specific_output_cv_l", "specific_output_kw_l", "power_per_cylinder_cv", "bmep_bar",
    "bmep_psi", "top_speed_kmh", "top_speed_mph", "acceleration_0_100_s",
    "acceleration_0_62_s", "power_to_weight_cv_ton", "power_to_weight_kw_ton",
    "fuel_consumption_urban_l_100km", "fuel_consumption_extraurban_l_100km",
    "fuel_consumption_combined_l_100km", "fuel_consumption_combined_mpg_uk",
    "fuel_consumption_combined_mpg_us", "co2_emissions_g_km", "emission_standard",
    "start_stop", "euro_ncap", "gearbox_type", "gearbox_label", "gear_count",
    "clutch_type", "front_suspension", "rear_suspension", "front_brakes", "rear_brakes",
    "steering_type", "turning_circle_m", "tyre_size", "front_tyre_size", "rear_tyre_size",
    "wheel_size", "front_wheel_size", "rear_wheel_size", "length_mm", "width_mm",
    "width_including_mirrors_mm", "height_mm", "wheelbase_mm", "front_track_mm",
    "rear_track_mm", "ground_clearance_mm", "kerb_weight_kg", "gross_weight_kg",
    "payload_kg", "towing_capacity_braked_kg", "towing_capacity_unbraked_kg",
    "boot_capacity_l", "boot_capacity_min_l", "boot_capacity_max_l", "fuel_tank_l",
    "match_key_manufacturer", "match_key_model", "match_key_generation", "match_key_version",
    "is_complete_minimum", "has_engine_block", "has_drivetrain_block", "has_dimensions_block",
    "has_performance_block", "has_weights_block"
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Migra T_Versiones a UNIQUE v2.")
    parser.add_argument("--db-path", required=True, help="Ruta a la base SQLite.")
    parser.add_argument(
        "--backup-path",
        required=False,
        help="Ruta de backup. Si no se indica, se crea junto a la DB."
    )
    args = parser.parse_args()

    db_path = Path(args.db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"No existe la base: {db_path}")

    backup_path = Path(args.backup_path) if args.backup_path else db_path.with_name(
        db_path.stem + "_backup_pre_t_versiones_unique_v2" + db_path.suffix
    )
    shutil.copy2(db_path, backup_path)
    print(f"[OK] Backup creado: {backup_path}")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF;")
    cur = conn.cursor()

    try:
        cur.execute("BEGIN TRANSACTION;")

        cur.execute("DROP TABLE IF EXISTS T_Versiones_new;")
        cur.execute(CREATE_T_VERSIONES_NEW)

        cols = ", ".join(ALL_COLUMNS)
        cur.execute(
            f"INSERT INTO T_Versiones_new ({cols}) SELECT {cols} FROM T_Versiones"
        )

        cur.execute("DROP TABLE T_Versiones;")
        cur.execute("ALTER TABLE T_Versiones_new RENAME TO T_Versiones;")

        for sql in RECREATE_INDEXES:
            cur.execute(sql)

        conn.commit()
        print("[OK] Migración completada.")
        print("[OK] UNIQUE nueva: (version_name_canonical, generation_id, production_start_year, production_end_year)")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
