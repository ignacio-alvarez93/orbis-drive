from src.catalogo.validacion_lote.lote_validator import LoteValidator


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
    assert result["metrics"]["conflicts"] >= 1
    assert any(issue["code"] == "conflict_same_version" for issue in result["errors"])


def test_same_base_with_different_explicit_period_is_not_conflict() -> None:
    records = [
        {
            "manufacturer_name": "SEAT",
            "model_name": "Leon",
            "generation_name": "Leon (2020-actualidad)",
            "version_name": "2.0 TDI 115",
            "production_start_year": 2020,
            "production_end_year": 2021,
            "power_cv": 115,
            "fuel_type": "Diesel",
            "gearbox_type": "MT",
        },
        {
            "manufacturer_name": "SEAT",
            "model_name": "Leon",
            "generation_name": "Leon (2020-actualidad)",
            "version_name": "2.0 TDI 115",
            "production_start_year": 2022,
            "production_end_year": 2024,
            "power_cv": 122,
            "fuel_type": "Diesel",
            "gearbox_type": "MT",
        },
    ]
    result = LoteValidator().validate(records).to_dict()
    assert result["is_valid_dataset"] is True
    assert result["metrics"]["conflicts"] == 0
    assert result["metrics"]["unique_versions"] == 2


def test_exact_duplicate_is_warning_not_error() -> None:
    records = [
        {
            "manufacturer_name": "SEAT",
            "model_name": "Ibiza",
            "generation_name": "Ibiza (2017-actualidad)",
            "version_name": "1.0 MPI 80",
            "production_start_year": 2019,
            "production_end_year": 2021,
            "power_cv": 80,
            "fuel_type": "Gasolina",
        },
        {
            "manufacturer_name": "SEAT",
            "model_name": "Ibiza",
            "generation_name": "Ibiza (2017-actualidad)",
            "version_name": "1.0 MPI 80",
            "production_start_year": 2019,
            "production_end_year": 2021,
            "power_cv": 80,
            "fuel_type": "Gasolina",
        },
    ]
    result = LoteValidator().validate(records).to_dict()
    assert result["is_valid_dataset"] is True
    assert result["metrics"]["duplicates"] == 1
    assert any(issue["code"] == "duplicate_exact" for issue in result["warnings"])
