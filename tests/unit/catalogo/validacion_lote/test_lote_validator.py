from __future__ import annotations

import json
from pathlib import Path

from src.catalogo.validacion_lote.lote_validator import LoteValidator


FIXTURE_PATH = Path("data/samples/input/lote_t_versiones.json")


def test_valid_dataset_has_no_errors() -> None:
    records = [
        {
            "manufacturer_name": "SEAT",
            "model_name": "Ibiza",
            "generation_name": "Ibiza (2002-2009)",
            "version_name": "Ibiza 1.2 12v 70",
            "power_cv": 70,
            "max_power_cv": 70,
            "fuel_type": "Gasolina",
            "gearbox_type": "MT",
            "gear_count": 5,
            "engine_displacement_l": 1.2,
            "engine_displacement_cc": 1198,
            "max_torque_nm": 112,
            "drive_type": "FWD",
            "boot_capacity_min_l": 267,
            "boot_capacity_max_l": 960,
        },
        {
            "manufacturer_name": "SEAT",
            "model_name": "Ibiza",
            "generation_name": "Ibiza (2002-2009)",
            "version_name": "Ibiza 1.4 16v 100",
            "power_cv": 100,
            "max_power_cv": 100,
            "fuel_type": "Gasolina",
            "gearbox_type": "MT",
            "gear_count": 5,
            "engine_displacement_l": 1.4,
            "engine_displacement_cc": 1390,
            "max_torque_nm": 126,
            "drive_type": "FWD",
            "boot_capacity_min_l": 267,
            "boot_capacity_max_l": 960,
        },
    ]
    result = LoteValidator().validate(records).to_dict()
    assert result["is_valid_dataset"] is True
    assert result["errors"] == []


def test_duplicate_semantic_is_detected() -> None:
    records = [
        {
            "manufacturer_name": "SEAT",
            "model_name": "Ibiza",
            "generation_name": "Ibiza (1993-2002)",
            "version_name": "Ibiza 1.6 GTi",
            "power_cv": 100,
        },
        {
            "manufacturer_name": " seat ",
            "model_name": "IBIZA",
            "generation_name": "Ibiza (1993-2002)",
            "version_name": " Ibiza 1.6 GTI ",
            "power_cv": 100,
        },
    ]
    result = LoteValidator().validate(records).to_dict()
    assert any(issue["code"].startswith("duplicate_") for issue in result["warnings"])


def test_conflict_is_detected() -> None:
    records = [
        {
            "manufacturer_name": "SEAT",
            "model_name": "Ibiza",
            "generation_name": "Ibiza (2017-actualidad)",
            "version_name": "Ibiza 1.0 EcoTSI 110",
            "power_cv": 110,
            "fuel_type": "Gasolina",
            "gearbox_type": "MT",
        },
        {
            "manufacturer_name": "SEAT",
            "model_name": "Ibiza",
            "generation_name": "Ibiza (2017-actualidad)",
            "version_name": "Ibiza 1.0 EcoTSI 110",
            "power_cv": 115,
            "fuel_type": "Gasolina",
            "gearbox_type": "MT",
        },
    ]
    result = LoteValidator().validate(records).to_dict()
    assert result["is_valid_dataset"] is False
    assert any(issue["code"] == "conflict_same_version" for issue in result["errors"])


def test_outlier_is_detected() -> None:
    records = [
        {
            "manufacturer_name": "SEAT",
            "model_name": "Ibiza",
            "generation_name": "Ibiza (2017-actualidad)",
            "version_name": "Ibiza 1.0 EcoTSI 110",
            "boot_capacity_min_l": 355,
            "boot_capacity_max_l": 1,
        }
    ]
    result = LoteValidator().validate(records).to_dict()
    assert any(issue["code"] in {"outlier_value", "outlier_boot_range"} for issue in result["warnings"])


def test_nulls_are_tolerated() -> None:
    records = [
        {
            "manufacturer_name": "SEAT",
            "model_name": "Ibiza",
            "generation_name": "Ibiza (2008-2017)",
            "version_name": "Ibiza SC 1.4 TDI 80",
            "fuel_type": None,
            "engine_displacement_cc": None,
        },
        {
            "manufacturer_name": "SEAT",
            "model_name": "Ibiza",
            "generation_name": "Ibiza (2008-2017)",
            "version_name": "Ibiza Cupra 1.8 TSI",
            "fuel_type": "Gasolina",
            "engine_displacement_cc": 1798,
        },
    ]
    result = LoteValidator().validate(records).to_dict()
    assert isinstance(result["warnings"], list)


def test_real_input_file_is_processed() -> None:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    result = LoteValidator().validate(payload).to_dict()
    assert result["metrics"]["total_records"] == len(payload)
    assert result["metrics"]["duplicates"] >= 1
    assert result["metrics"]["conflicts"] >= 1
    assert result["metrics"]["warnings"] >= 1
