from src.catalogo.dvl.rules.engine_rules import validate_engine_rules


def test_engine_rules_detect_displacement_incoherence():
    record = {"engine_displacement_cc": 1600, "engine_displacement_l": 1.0}
    errors = []
    warnings = []
    validate_engine_rules(record, errors, warnings)
    assert "cilindrada incoherente entre cc y l" in warnings


def test_engine_rules_detect_suspicious_rpm():
    record = {"max_power_rpm": 110, "max_torque_nm": 200, "max_torque_rpm": 200}
    errors = []
    warnings = []
    validate_engine_rules(record, errors, warnings)
    assert "max_power_rpm: sospechosamente bajo" in warnings
    assert "max_torque_rpm: sospechosamente bajo" in warnings
