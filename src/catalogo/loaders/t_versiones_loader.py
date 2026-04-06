from __future__ import annotations

from src.catalogo.loaders.ingestion_report import RecordResult
from src.catalogo.loaders.reference_resolver import ResolvedReferences


class TVersionesLoader:
    """
    Loader v2 para T_Versiones.

    Principios:
    - Mantiene el control anti-duplicado probado por (version_name_canonical, generation_id)
    - Inserta todas las columnas reales de T_Versiones que existan en el dataset resuelto
    - No inventa datos: si el campo no existe en el row, persiste NULL
    """

    BASE_COLUMNS = [
        "version_id",
        "manufacturer_id",
        "model_id",
        "generation_id",
    ]

    DATASET_COLUMNS = [
        "source",
        "source_version_url",
        "source_version_url_canonical",
        "source_generation_url",
        "source_model_url",
        "source_manufacturer_url",
        "scrape_date",
        "scrape_timestamp",
        "html_lang",
        "source_date_modified",
        "manufacturer_name",
        "manufacturer_name_upper",
        "model_name",
        "model_name_upper",
        "generation_name",
        "generation_name_canonical",
        "generation_name_upper",
        "version_name",
        "version_name_canonical",
        "version_name_upper",
        "full_title",
        "headline",
        "meta_description",
        "body_type",
        "trim",
        "facelift_status",
        "doors",
        "seats",
        "production_start_year",
        "production_end_year",
        "production_years_text",
        "model_year",
        "is_current_generation",
        "power_cv",
        "power_bhp",
        "fuel_type",
        "drive_type",
        "drive_type_label",
        "engine_name",
        "engine_code",
        "engine_family",
        "engine_type",
        "engine_layout",
        "cylinders",
        "valves_total",
        "valves_per_cylinder",
        "valvetrain",
        "aspiration",
        "fuel_system",
        "engine_position",
        "engine_orientation",
        "engine_displacement_cc",
        "engine_displacement_l",
        "unitary_displacement_cc",
        "compression_ratio",
        "bore_mm",
        "stroke_mm",
        "bore_stroke_text",
        "bore_stroke_ratio",
        "bore_stroke_ratio_label",
        "max_power_cv",
        "max_power_kw",
        "max_power_bhp",
        "max_power_rpm",
        "max_torque_nm",
        "max_torque_lbft",
        "max_torque_rpm",
        "specific_output_cv_l",
        "specific_output_kw_l",
        "power_per_cylinder_cv",
        "bmep_bar",
        "bmep_psi",
        "top_speed_kmh",
        "top_speed_mph",
        "acceleration_0_100_s",
        "acceleration_0_62_s",
        "power_to_weight_cv_ton",
        "power_to_weight_kw_ton",
        "fuel_consumption_urban_l_100km",
        "fuel_consumption_extraurban_l_100km",
        "fuel_consumption_combined_l_100km",
        "fuel_consumption_combined_mpg_uk",
        "fuel_consumption_combined_mpg_us",
        "co2_emissions_g_km",
        "emission_standard",
        "start_stop",
        "euro_ncap",
        "gearbox_type",
        "gearbox_label",
        "gear_count",
        "clutch_type",
        "front_suspension",
        "rear_suspension",
        "front_brakes",
        "rear_brakes",
        "steering_type",
        "turning_circle_m",
        "tyre_size",
        "front_tyre_size",
        "rear_tyre_size",
        "wheel_size",
        "front_wheel_size",
        "rear_wheel_size",
        "length_mm",
        "width_mm",
        "width_including_mirrors_mm",
        "height_mm",
        "wheelbase_mm",
        "front_track_mm",
        "rear_track_mm",
        "ground_clearance_mm",
        "kerb_weight_kg",
        "gross_weight_kg",
        "payload_kg",
        "towing_capacity_braked_kg",
        "towing_capacity_unbraked_kg",
        "boot_capacity_l",
        "boot_capacity_min_l",
        "boot_capacity_max_l",
        "fuel_tank_l",
        "match_key_manufacturer",
        "match_key_model",
        "match_key_generation",
        "match_key_version",
        "is_complete_minimum",
        "has_engine_block",
        "has_drivetrain_block",
        "has_dimensions_block",
        "has_performance_block",
        "has_weights_block",
    ]

    def __init__(self, conn):
        self.conn = conn
        self._table_columns = self._get_table_columns("T_Versiones")

    def _get_table_columns(self, table_name: str) -> set[str]:
        rows = self.conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        return {row[1] for row in rows}

    def exists(self, version_name_canonical: str, generation_id: str) -> bool:
        cur = self.conn.execute(
            """
            SELECT 1
            FROM T_Versiones
            WHERE version_name_canonical = ?
              AND generation_id = ?
            LIMIT 1
            """,
            (version_name_canonical, generation_id),
        )
        return cur.fetchone() is not None

    def _coalesce_aliases(self, row: dict) -> dict:
        normalized = dict(row)

        if normalized.get("gearbox_type") is None and normalized.get("gearbox") is not None:
            normalized["gearbox_type"] = normalized.get("gearbox")

        if normalized.get("drive_type") is None and normalized.get("traction") is not None:
            normalized["drive_type"] = normalized.get("traction")

        return normalized

    def _build_insert_payload(self, row: dict, refs: ResolvedReferences) -> tuple[list[str], list]:
        normalized = self._coalesce_aliases(row)

        payload = {
            "version_id": normalized.get("version_id"),
            "manufacturer_id": refs.manufacturer_id,
            "model_id": refs.model_id,
            "generation_id": refs.generation_id,
        }

        for col in self.DATASET_COLUMNS:
            payload[col] = normalized.get(col)

        insert_columns = [c for c in (self.BASE_COLUMNS + self.DATASET_COLUMNS) if c in self._table_columns]
        insert_values = [payload.get(c) for c in insert_columns]
        return insert_columns, insert_values

    def insert_one(
        self,
        row_index: int,
        row: dict,
        refs: ResolvedReferences,
        ingestion_run_id: str,
    ) -> RecordResult:
        version_id = row.get("version_id")
        version_name = row.get("version_name")
        version_name_canonical = row.get("version_name_canonical")

        if not version_id:
            raise ValueError("Falta 'version_id' en el dataset resuelto.")
        if not version_name_canonical:
            raise ValueError("Falta 'version_name_canonical' en el dataset resuelto.")

        duplicate_key = f"{version_name_canonical}|{refs.generation_id}"

        if self.exists(version_name_canonical, refs.generation_id):
            return RecordResult(
                row_index=row_index,
                status="skipped_duplicate",
                table="T_Versiones",
                semantic_key=duplicate_key,
                message="Registro omitido por duplicado según (version_name_canonical, generation_id).",
                record_ref={
                    "version_id": version_id,
                    "manufacturer_id": refs.manufacturer_id,
                    "model_id": refs.model_id,
                    "generation_id": refs.generation_id,
                    "version_name": version_name,
                },
            )

        insert_columns, insert_values = self._build_insert_payload(row, refs)
        placeholders = ", ".join(["?"] * len(insert_columns))
        sql = f"""
            INSERT INTO T_Versiones (
                {", ".join(insert_columns)}
            ) VALUES ({placeholders})
        """

        self.conn.execute(sql, insert_values)

        return RecordResult(
            row_index=row_index,
            status="inserted",
            table="T_Versiones",
            semantic_key=duplicate_key,
            message="Registro insertado correctamente.",
            record_ref={
                "version_id": version_id,
                "manufacturer_id": refs.manufacturer_id,
                "model_id": refs.model_id,
                "generation_id": refs.generation_id,
                "version_name": version_name,
            },
        )
