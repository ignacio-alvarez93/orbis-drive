from src.catalogo.dvl.rules.identity_rules import normalize_identity_fields, validate_identity_rules


def test_identity_normalization_uppercases_core_fields():
    record = {
        "manufacturer_name": " Seat ",
        "model_name": "ibiza",
        "generation_name": "6j",
        "version_name": "1.0 tsi style",
        "fuel_type": "Gasolina",
        "gearbox_type": "AT",
        "body_type": "Pequeño Hatchback",
        "drive_type": "FWD",
    }
    normalize_identity_fields(record)
    assert record["manufacturer_name"] == "SEAT"
    assert record["model_name"] == "IBIZA"
    assert record["version_name"] == "1.0 TSI STYLE"
    assert record["fuel_type"] == "gasoline"
    assert record["gearbox_type"] == "automatic"
    assert record["body_type"] == "hatchback"
    assert record["drive_type"] == "fwd"


def test_identity_validation_detects_missing_critical():
    record = {
        "manufacturer_name": "SEAT",
        "model_name": "IBIZA",
        "version_name": None,
        "fuel_type": "gasoline",
    }
    errors = []
    warnings = []
    validate_identity_rules(record, errors, warnings)
    assert "version_name: campo crítico ausente o inválido" in errors
