-- Orbis Drive
-- Schema generado desde Orbis_Drive.db
-- Bloque 001: tablas core y catálogo base
-- Orden de ejecución: 001

PRAGMA foreign_keys = ON;

CREATE TABLE T_Fabricantes (
    manufacturer_id TEXT PRIMARY KEY,
    manufacturer_name TEXT,
    manufacturer_name_upper TEXT,
    manufacturer_href_relative TEXT,
    manufacturer_href_absolute TEXT
);

CREATE TABLE T_Modelos (
    manufacturer_id TEXT NOT NULL,
    manufacturer_name TEXT,
    manufacturer_name_upper TEXT,
    model_id TEXT PRIMARY KEY,
    model_name TEXT,
    model_name_upper TEXT,
    model_href_relative TEXT,
    model_href_absolute TEXT,
    CONSTRAINT fk_modelos_manufacturer
        FOREIGN KEY (manufacturer_id) REFERENCES T_Fabricantes(manufacturer_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT uq_modelos_manufacturer_model_name
        UNIQUE (manufacturer_id, model_name)
);

CREATE TABLE T_Generaciones (
    manufacturer_id TEXT NOT NULL,
    manufacturer_name TEXT,
    manufacturer_name_upper TEXT,
    model_id TEXT NOT NULL,
    model_name TEXT,
    model_name_upper TEXT,
    generation_id TEXT PRIMARY KEY,
    generation_name TEXT,
    generation_name_canonical TEXT,
    generation_name_upper TEXT,
    year_start INTEGER,
    year_end TEXT,
    year_end_raw TEXT,
    generation_href_relative TEXT,
    generation_href_absolute TEXT,
    CONSTRAINT fk_generaciones_model
        FOREIGN KEY (model_id) REFERENCES T_Modelos(model_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_generaciones_manufacturer
        FOREIGN KEY (manufacturer_id) REFERENCES T_Fabricantes(manufacturer_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT uq_generaciones_model_generation_name
        UNIQUE (model_id, generation_name)
);

CREATE TABLE T_Versiones (
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

    UNIQUE (version_name_canonical, generation_id)
);
