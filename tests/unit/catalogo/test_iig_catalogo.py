from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from src.catalogo.iig.iig_catalogo import IIG_Catalogo


@pytest.fixture()
def contract_path() -> Path:
    return Path(__file__).resolve().parents[3] / "contracts" / "catalogo" / "t_versiones.contract.json"


@pytest.fixture()
def iig(contract_path: Path) -> IIG_Catalogo:
    return IIG_Catalogo(contract_path=contract_path, mode="observacion")


@pytest.fixture()
def base_record() -> Dict[str, Any]:
    return {
        "version_id": "seat_ibiza_2021_1.0_tsi_95_style",
        "manufacturer_id": "seat",
        "model_id": "ibiza",
        "generation_id": "ibiza_kj_2021",
        "source": "encycarpedia",
        "source_version_url": "https://example.com/seat-ibiza-version",
        "manufacturer_name": "SEAT",
        "model_name": "Ibiza",
        "generation_name": "KJ 2021",
        "version_name": "1.0 TSI 95 Style",
        "power_cv": 95,
        "fuel_type": "petrol",
        "gearbox_type": "manual",
        "engine_displacement_cc": 999,
        "scrape_date": "2026-03-28",
        "scrape_timestamp": "2026-03-28T10:15:00Z",
    }


def test_validate_record_ok(iig: IIG_Catalogo, base_record: Dict[str, Any]) -> None:
    result = iig.validate_record(base_record)

    assert result.is_valid is True
    assert result.flags.has_errors is False
    assert result.flags.should_block is False
    assert result.original_record == base_record


def test_detects_extra_keys(iig: IIG_Catalogo, base_record: Dict[str, Any]) -> None:
    record = dict(base_record)
    record["campo_inventado"] = "ruido"

    result = iig.validate_record(record)

    codes = {error.code for error in result.errors}
    assert "extra_keys" in codes
    assert result.flags.has_critical is True
    assert result.flags.should_block is True


def test_detects_missing_minimum_fields(iig: IIG_Catalogo, base_record: Dict[str, Any]) -> None:
    record = dict(base_record)
    record["source_version_url"] = ""

    result = iig.validate_record(record)

    codes = {error.code for error in result.errors}
    assert "missing_minimum_fields" in codes
    assert result.flags.minimum_fields_valid is False


def test_detects_invalid_types(iig: IIG_Catalogo, base_record: Dict[str, Any]) -> None:
    record = dict(base_record)
    record["power_cv"] = "95"
    record["version_name"] = 123

    result = iig.validate_record(record)

    invalid_type_fields = {error.field for error in result.errors if error.code == "invalid_type"}
    assert "power_cv" in invalid_type_fields
    assert "version_name" in invalid_type_fields
    assert result.flags.types_valid is False


def test_detects_invalid_date_and_datetime(iig: IIG_Catalogo, base_record: Dict[str, Any]) -> None:
    record = dict(base_record)
    record["scrape_date"] = "28/03/2026"
    record["scrape_timestamp"] = "ayer"

    result = iig.validate_record(record)

    codes = {error.code for error in result.errors}
    assert "invalid_date" in codes
    assert "invalid_datetime" in codes


def test_warns_for_low_technical_content(iig: IIG_Catalogo, base_record: Dict[str, Any]) -> None:
    record = dict(base_record)
    for field_name in ["power_cv", "fuel_type", "gearbox_type", "engine_displacement_cc"]:
        record[field_name] = None

    result = iig.validate_record(record)

    warning_codes = {warning.code for warning in result.warnings}
    assert "low_technical_content" in warning_codes
    assert result.flags.low_technical_content_warning is True


def test_batch_summary(iig: IIG_Catalogo, base_record: Dict[str, Any]) -> None:
    bad_record = dict(base_record)
    bad_record["campo_inventado"] = "ruido"
    bad_record["power_cv"] = "95"

    batch_result = iig.validate_batch([base_record, bad_record])

    assert batch_result.total_records == 2
    assert batch_result.valid_records == 1
    assert batch_result.records_with_errors == 1
    assert "extra_keys" in batch_result.error_summary
    assert "critical_records_present" in batch_result.anomaly_flags


def test_strict_mode_blocks_any_error(contract_path: Path, base_record: Dict[str, Any]) -> None:
    iig = IIG_Catalogo(contract_path=contract_path, mode="estricto")
    record = dict(base_record)
    record["power_cv"] = "95"

    result = iig.validate_record(record)

    assert result.flags.has_errors is True
    assert result.flags.should_block is True
