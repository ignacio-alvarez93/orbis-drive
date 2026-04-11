from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Dict, Iterable, List, Optional

from src.catalogo.enrichment.models.enrichment_result import EnrichmentResult
from src.catalogo.enrichment.rules.boot_rules import derive_boot_capacity_range
from src.catalogo.enrichment.rules.gearbox_rules import derive_gearbox_type
from src.catalogo.enrichment.rules.generation_rules import derive_is_current_generation
from src.catalogo.enrichment.rules.trim_rules import derive_trim_from_version_name

RuleFn = Callable[[Dict[str, Any]], Optional[Dict[str, Dict[str, Any]]]]


class EnrichmentEngine:
    """
    Motor modular de enriquecimiento semántico.
    Ejecuta reglas deterministas sobre datos ya validados.
    """

    def __init__(self, rules: Optional[Iterable[RuleFn]] = None) -> None:
        self.rules: List[RuleFn] = list(rules) if rules else self._default_rules()

    def _default_rules(self) -> List[RuleFn]:
        return [
            derive_gearbox_type,
            derive_boot_capacity_range,
            derive_trim_from_version_name,
            derive_is_current_generation,
        ]

    def run(self, validated_dict: Dict[str, Any]) -> EnrichmentResult:
        safe_input = deepcopy(validated_dict)
        result = EnrichmentResult(original_data=safe_input)

        for rule in self.rules:
            output = rule(safe_input)
            result.applied_rules.append(f"{rule.__module__.split('.')[-1]}.{rule.__name__}")

            if not output:
                continue

            for field_name, payload in output.items():
                result.add_field(
                    field_name=field_name,
                    value=payload["value"],
                    source=payload["source"],
                    rule=payload["rule"],
                    confidence="deterministic",
                )

        return result.finalize()
