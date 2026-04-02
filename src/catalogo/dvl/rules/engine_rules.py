from __future__ import annotations

from typing import Any, Dict, List, Optional


def validate_engine_rules(record: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
    engine_displacement_cc = _to_float(record.get("engine_displacement_cc"))
    engine_displacement_l = _to_float(record.get("engine_displacement_l"))
    max_power_rpm = _to_float(record.get("max_power_rpm"))
    max_torque_nm = _to_float(record.get("max_torque_nm"))
    max_torque_rpm = _to_float(record.get("max_torque_rpm"))
    cylinders = _to_float(record.get("cylinders"))
    unitary_displacement_cc = _to_float(record.get("unitary_displacement_cc"))

    if record.get("engine_displacement_cc") is not None:
        if engine_displacement_cc is None:
            warnings.append("engine_displacement_cc: tipo inválido")
        elif engine_displacement_cc <= 0:
            warnings.append("engine_displacement_cc: valor no positivo")

    if record.get("engine_displacement_l") is not None:
        if engine_displacement_l is None:
            warnings.append("engine_displacement_l: tipo inválido")
        elif engine_displacement_l <= 0:
            warnings.append("engine_displacement_l: valor no positivo")

    if engine_displacement_cc is not None and engine_displacement_l is not None:
        expected_cc = engine_displacement_l * 1000.0
        if abs(engine_displacement_cc - expected_cc) > max(80.0, expected_cc * 0.05):
            warnings.append("cilindrada incoherente entre cc y l")

    if cylinders is not None and unitary_displacement_cc is not None and engine_displacement_l is not None:
        expected_unitary_cc = (engine_displacement_l * 1000.0) / cylinders
        if abs(unitary_displacement_cc - expected_unitary_cc) > max(25.0, expected_unitary_cc * 0.08):
            warnings.append("unitary_displacement_cc incoherente con cilindrada y cilindros")

    if record.get("max_power_rpm") is not None:
        if max_power_rpm is None:
            warnings.append("max_power_rpm: tipo inválido")
        elif max_power_rpm <= 0:
            warnings.append("max_power_rpm: valor no positivo")
        elif max_power_rpm < 500:
            warnings.append("max_power_rpm: sospechosamente bajo")
        elif max_power_rpm > 15000:
            warnings.append("max_power_rpm: sospechosamente alto")

    if max_torque_nm is not None and max_torque_rpm is None:
        warnings.append("max_torque_nm presente sin max_torque_rpm")
    if max_torque_rpm is not None and max_torque_nm is None:
        warnings.append("max_torque_rpm presente sin max_torque_nm")
    if max_torque_rpm is not None and max_torque_rpm < 250:
        warnings.append("max_torque_rpm: sospechosamente bajo")


def _to_float(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None
