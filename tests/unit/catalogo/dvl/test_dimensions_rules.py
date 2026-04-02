from src.catalogo.dvl.rules.dimensions_rules import normalize_dimensions_fields, validate_dimensions_rules


def test_dimensions_normalizer_keeps_range_string_for_doors():
    record = {"doors": "3-5"}
    normalize_dimensions_fields(record)
    assert record["doors"] == "3-5"


def test_dimensions_rules_flag_absurd_boot_capacity_as_warning():
    record = {"boot_capacity_max_l": 1}
    errors = []
    warnings = []
    validate_dimensions_rules(record, errors, warnings)
    assert "boot_capacity_max_l: sospechosamente bajo" in warnings
