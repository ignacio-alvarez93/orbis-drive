from __future__ import annotations

import inspect
from typing import Any, Callable

from src.catalogo.enrichment.models.enrichment_result import EnrichmentResult
from src.catalogo.enrichment.rules import (
    derive_boot_capacity_range,
    derive_fuel_consumption_combined_mpg_uk,
    derive_fuel_consumption_combined_mpg_us,
    derive_gearbox_type,
    derive_is_current_generation,
    derive_max_power_kw,
    derive_power_to_weight_cv_ton,
    derive_power_to_weight_kw_ton,
    derive_specific_output_kw_l,
    derive_top_speed_mph,
    derive_trim_from_version_name,
)

Rule = Callable[..., Any]


class EnrichmentEngine:
    """
    ESL v1 + ESL v2

    Posición oficial en pipeline:
    DVL -> VALIDACIÓN DE LOTE -> ENRICHMENT -> ID_RESOLUTION -> INGESTIÓN

    Compatibilidad:
    - ESL v1: reglas que reciben solo `data` y devuelven dict legacy
    - ESL v2: reglas que reciben `data, result` y escriben sobre EnrichmentResult
    """

    def __init__(self, rules: list[Rule] | None = None) -> None:
        self.rules = rules or [
            derive_gearbox_type,
            derive_boot_capacity_range,
            derive_trim_from_version_name,
            derive_is_current_generation,
            derive_max_power_kw,
            derive_specific_output_kw_l,
            derive_top_speed_mph,
            derive_power_to_weight_cv_ton,
            derive_power_to_weight_kw_ton,
            derive_fuel_consumption_combined_mpg_uk,
            derive_fuel_consumption_combined_mpg_us,
        ]

    def _apply_legacy_output(
        self,
        rule: Rule,
        legacy_output: dict[str, Any],
        result: EnrichmentResult,
    ) -> None:
        rule_name = f"{rule.__module__.split('.')[-1]}.{rule.__name__}"

        for field_name, raw_value in legacy_output.items():
            if isinstance(raw_value, dict) and "value" in raw_value:
                value = raw_value.get("value")
                source = raw_value.get("source", "legacy_rule")
                trace_rule = raw_value.get("rule", rule_name)
                confidence = raw_value.get("confidence", "deterministic")
            else:
                value = raw_value
                source = "legacy_rule"
                trace_rule = rule_name
                confidence = "deterministic"

            result.add_field(
                field_name=field_name,
                value=value,
                source=source,
                rule=trace_rule,
                confidence=confidence,
            )

    def _apply_rule(self, rule: Rule, validated_dict: dict[str, Any], result: EnrichmentResult) -> None:
        signature = inspect.signature(rule)
        param_count = len(signature.parameters)

        if param_count == 1:
            legacy_output = rule(validated_dict)
            if isinstance(legacy_output, dict):
                self._apply_legacy_output(rule, legacy_output, result)
            return

        rule(validated_dict, result)

    def run(self, validated_dict: dict[str, Any]) -> EnrichmentResult:
        result = EnrichmentResult(original_data=dict(validated_dict))

        for rule in self.rules:
            rule_name = f"{rule.__module__.split('.')[-1]}.{rule.__name__}"
            result.applied_rules.append(rule_name)
            self._apply_rule(rule, validated_dict, result)

        return result.finalize()
