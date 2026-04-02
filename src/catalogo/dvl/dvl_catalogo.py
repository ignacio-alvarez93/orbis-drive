from __future__ import annotations

from typing import Any, Dict

from src.catalogo.dvl.core.result_model import ValidationResult
from src.catalogo.dvl.core.validator_engine import ValidatorEngine
from src.catalogo.dvl.metrics.completeness import build_completeness_metrics
from src.catalogo.dvl.rules.dimensions_rules import normalize_dimensions_fields, validate_dimensions_rules
from src.catalogo.dvl.rules.engine_rules import validate_engine_rules
from src.catalogo.dvl.rules.identity_rules import normalize_identity_fields, validate_identity_rules
from src.catalogo.dvl.rules.performance_rules import validate_performance_rules


class DVL_Catalogo:
    """Motor universal de validación semántica para T_Versiones.

    Principios:
    - no infiere
    - no corrige
    - no reconstruye
    - no bloquea por campos no críticos
    - solo bloquea si falla la verdad mínima crítica del registro
    """

    def __init__(self) -> None:
        self.engine = ValidatorEngine(
            normalizers=[
                normalize_identity_fields,
                normalize_dimensions_fields,
            ],
            rules=[
                validate_identity_rules,
                validate_engine_rules,
                validate_performance_rules,
                validate_dimensions_rules,
            ],
            metrics_builder=build_completeness_metrics,
        )

    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        return self.engine.validate(record)


if __name__ == "__main__":
    sample_record = {
        "manufacturer_name": " Seat ",
        "model_name": "ibiza",
        "generation_name": "6j",
        "version_name": "1.0 tsi style",
        "fuel_type": "Gasolina",
        "gearbox_type": "MT",
        "gear_count": 5,
        "power_cv": 95,
        "max_power_cv": 95,
        "max_power_rpm": 5500,
        "engine_displacement_cc": 999,
        "engine_displacement_l": 1.0,
        "max_torque_nm": 175,
        "max_torque_rpm": 2000,
        "doors": "3-5",
        "seats": "5",
        "boot_capacity_max_l": 355,
        "body_type": "Pequeño Hatchback",
        "drive_type": "FWD",
    }

    dvl = DVL_Catalogo()
    result = dvl.validate(sample_record)

    print({
        "is_valid": result.is_valid,
        "errors": result.errors,
        "warnings": result.warnings,
        "normalized_data": result.normalized_data,
        "metrics": result.metrics,
    })
