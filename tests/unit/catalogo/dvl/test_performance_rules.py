from src.catalogo.dvl.rules.performance_rules import validate_performance_rules


def test_performance_rules_detect_power_incoherence():
    record = {"power_cv": 100, "max_power_kw": 10}
    errors = []
    warnings = []
    validate_performance_rules(record, errors, warnings)
    assert "potencia incoherente entre CV y kW" in warnings
