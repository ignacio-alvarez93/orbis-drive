from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Dict, Iterable, List

from src.catalogo.dvl.core.result_model import ValidationResult

RuleFn = Callable[[Dict[str, Any], List[str], List[str]], None]
NormalizerFn = Callable[[Dict[str, Any]], None]
MetricsBuilderFn = Callable[[Dict[str, Any], List[str], List[str]], Dict[str, Any]]


class ValidatorEngine:
    """Motor central de ejecución de normalizadores y reglas.

    Orden:
    1. clona el registro
    2. aplica normalizadores conservadores
    3. ejecuta reglas modulares
    4. calcula métricas
    5. devuelve ValidationResult
    """

    def __init__(
        self,
        rules: Iterable[RuleFn],
        normalizers: Iterable[NormalizerFn],
        metrics_builder: MetricsBuilderFn,
    ) -> None:
        self.rules = list(rules)
        self.normalizers = list(normalizers)
        self.metrics_builder = metrics_builder

    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        normalized = deepcopy(record)
        errors: List[str] = []
        warnings: List[str] = []

        for normalizer in self.normalizers:
            normalizer(normalized)

        for rule in self.rules:
            rule(normalized, errors, warnings)

        metrics = self.metrics_builder(normalized, errors, warnings)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            normalized_data=normalized,
            metrics=metrics,
        )
