import pytest

from src.catalogo.dvl.dvl_catalogo import DVL_Catalogo


@pytest.fixture
def dvl():
    return DVL_Catalogo()


def test_valid_record_passes(dvl):
    record = {
        "manufacturer_name": "Seat",
        "model_name": "Ibiza",
        "version_name": "1.0 TSI Style",
        "fuel_type": "Gasolina",
        "power_cv": 95,
        "engine_displacement_cc": 999,
        "engine_displacement_l": 1.0,
        "gearbox_type": "MT",
        "gear_count": 5,
        "doors": "5",
        "boot_capacity_max_l": 355,
    }
    result = dvl.validate(record)
    assert result.is_valid is True
    assert result.errors == []
    assert result.normalized_data["manufacturer_name"] == "SEAT"
    assert result.normalized_data["fuel_type"] == "gasoline"
    assert result.normalized_data["gearbox_type"] == "manual"
    assert result.normalized_data["doors"] == 5


def test_missing_critical_field_blocks_record(dvl):
    record = {
        "manufacturer_name": "Seat",
        "model_name": "Ibiza",
        "version_name": None,
        "fuel_type": "Gasolina",
    }
    result = dvl.validate(record)
    assert result.is_valid is False
    assert "version_name: campo crítico ausente o inválido" in result.errors


def test_missing_relevant_field_does_not_block(dvl):
    record = {
        "manufacturer_name": "Seat",
        "model_name": "Ibiza",
        "version_name": "1.0 TSI",
        "fuel_type": "Gasolina",
        "power_cv": None,
        "engine_displacement_cc": None,
    }
    result = dvl.validate(record)
    assert result.is_valid is True


def test_unknown_enum_becomes_none_and_blocks_if_critical(dvl):
    record = {
        "manufacturer_name": "Seat",
        "model_name": "Ibiza",
        "version_name": "1.0 TSI",
        "fuel_type": "combustible marciano",
    }
    result = dvl.validate(record)
    assert result.is_valid is False
    assert result.normalized_data["fuel_type"] is None


def test_doors_range_string_is_preserved(dvl):
    record = {
        "manufacturer_name": "Ford",
        "model_name": "Transit",
        "version_name": "Combi",
        "fuel_type": "diesel",
        "doors": "3-5",
    }
    result = dvl.validate(record)
    assert result.is_valid is True
    assert result.normalized_data["doors"] == "3-5"


def test_absurd_boot_capacity_generates_warning(dvl):
    record = {
        "manufacturer_name": "Seat",
        "model_name": "Ibiza",
        "version_name": "1.0 TSI",
        "fuel_type": "gasoline",
        "boot_capacity_max_l": 1,
    }
    result = dvl.validate(record)
    assert result.is_valid is True
    assert "boot_capacity_max_l: sospechosamente bajo" in result.warnings


def test_max_power_rpm_suspicious_low_generates_warning(dvl):
    record = {
        "manufacturer_name": "Seat",
        "model_name": "Ibiza",
        "version_name": "1.0 TSI",
        "fuel_type": "gasoline",
        "max_power_rpm": 192,
    }
    result = dvl.validate(record)
    assert result.is_valid is True
    assert "max_power_rpm: sospechosamente bajo" in result.warnings


def test_metrics_are_returned(dvl):
    record = {
        "manufacturer_name": "Seat",
        "model_name": "Ibiza",
        "version_name": "1.0 TSI",
        "fuel_type": "gasoline",
    }
    result = dvl.validate(record)
    assert "completeness_score" in result.metrics
    assert "critical_ok_ratio" in result.metrics
    assert "warning_count" in result.metrics
    assert "error_count" in result.metrics
