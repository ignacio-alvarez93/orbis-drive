
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class IIGIssue:
    code: str
    message: str
    field: str | None = None


@dataclass(slots=True)
class IIGRowResult:
    row_index: int
    is_valid: bool
    errors: list[IIGIssue] = field(default_factory=list)


@dataclass(slots=True)
class IIGBatchResult:
    entity: str
    contract_name: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    results: list[IIGRowResult]

    @property
    def is_valid_batch(self) -> bool:
        return self.invalid_rows == 0


class IIGLocalizacion:
    """
    Guardián estructural del contrato territorial.

    Responsabilidades:
    - validar esquema
    - validar campos obligatorios
    - validar tipos
    - rechazar desviaciones estructurales

    Prohibido:
    - normalizar
    - mapear
    - inferir
    """

    def __init__(self, contract_path: str | Path) -> None:
        self.contract_path = Path(contract_path)
        self.contract = self._load_contract(self.contract_path)

        self.contract_name: str = self.contract["contract_name"]
        self.entity: str = self.contract["entity"]
        self.strict_mode: bool = bool(self.contract.get("strict_mode", True))
        self.additional_properties: bool = bool(
            self.contract.get("additional_properties", False)
        )
        self.required_fields: set[str] = set(self.contract.get("required_fields", []))
        self.optional_fields: set[str] = set(self.contract.get("optional_fields", []))
        self.fields: dict[str, dict[str, Any]] = self.contract.get("fields", {})

        self.allowed_fields: set[str] = set(self.fields.keys())

    def validate_rows(self, rows: list[dict[str, Any]]) -> IIGBatchResult:
        results: list[IIGRowResult] = []

        for idx, row in enumerate(rows, start=1):
            # Prioriza el índice real propagado por STAGING para mantener trazabilidad exacta.
            real_row_index = row.get("_row_index", idx)
            row_result = self.validate_row(row=row, row_index=real_row_index)
            results.append(row_result)

        valid_rows = sum(1 for r in results if r.is_valid)
        invalid_rows = len(results) - valid_rows

        return IIGBatchResult(
            entity=self.entity,
            contract_name=self.contract_name,
            total_rows=len(rows),
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            results=results,
        )

    def validate_row(self, row: dict[str, Any], row_index: int) -> IIGRowResult:
        errors: list[IIGIssue] = []

        if not isinstance(row, dict):
            return IIGRowResult(
                row_index=row_index,
                is_valid=False,
                errors=[
                    IIGIssue(
                        code="row_not_dict",
                        message="La fila debe ser un diccionario.",
                    )
                ],
            )

        known_meta_fields = {"_source_file", "_row_index"}
        user_fields = set(row.keys()) - known_meta_fields

        if self.strict_mode and not self.additional_properties:
            unknown_fields = sorted(user_fields - self.allowed_fields)
            for field_name in unknown_fields:
                errors.append(
                    IIGIssue(
                        code="unknown_field",
                        field=field_name,
                        message=f"Campo no permitido por contrato: '{field_name}'.",
                    )
                )

        for field_name in sorted(self.required_fields):
            if field_name not in row:
                errors.append(
                    IIGIssue(
                        code="missing_required_field",
                        field=field_name,
                        message=f"Falta el campo obligatorio '{field_name}'.",
                    )
                )

        for field_name, field_rules in self.fields.items():
            if field_name not in row:
                continue

            value = row[field_name]
            field_errors = self._validate_field_value(field_name, value, field_rules)
            errors.extend(field_errors)

        return IIGRowResult(
            row_index=row_index,
            is_valid=len(errors) == 0,
            errors=errors,
        )

    def _validate_field_value(
        self,
        field_name: str,
        value: Any,
        field_rules: dict[str, Any],
    ) -> list[IIGIssue]:
        issues: list[IIGIssue] = []

        expected_type = field_rules.get("type")
        allow_null = bool(field_rules.get("allow_null", False))
        allow_empty = bool(field_rules.get("allow_empty", False))
        min_length = field_rules.get("min_length")
        max_length = field_rules.get("max_length")
        pattern = field_rules.get("pattern")

        if value is None:
            if not allow_null:
                issues.append(
                    IIGIssue(
                        code="null_not_allowed",
                        field=field_name,
                        message=f"El campo '{field_name}' no admite NULL.",
                    )
                )
            return issues

        if expected_type == "string":
            if not isinstance(value, str):
                issues.append(
                    IIGIssue(
                        code="invalid_type",
                        field=field_name,
                        message=(
                            f"El campo '{field_name}' debe ser string, "
                            f"recibido: {type(value).__name__}."
                        ),
                    )
                )
                return issues

            if not allow_empty and value == "":
                issues.append(
                    IIGIssue(
                        code="empty_string_not_allowed",
                        field=field_name,
                        message=f"El campo '{field_name}' no admite string vacío.",
                    )
                )
                return issues

            if min_length is not None and len(value) < int(min_length):
                issues.append(
                    IIGIssue(
                        code="min_length_violation",
                        field=field_name,
                        message=(
                            f"El campo '{field_name}' tiene longitud menor a {min_length}."
                        ),
                    )
                )

            if max_length is not None and len(value) > int(max_length):
                issues.append(
                    IIGIssue(
                        code="max_length_violation",
                        field=field_name,
                        message=(
                            f"El campo '{field_name}' tiene longitud mayor a {max_length}."
                        ),
                    )
                )

            if pattern:
                import re

                if re.fullmatch(pattern, value) is None:
                    issues.append(
                        IIGIssue(
                            code="pattern_violation",
                            field=field_name,
                            message=(
                                f"El campo '{field_name}' no cumple el patrón '{pattern}'."
                            ),
                        )
                    )

            return issues

        issues.append(
            IIGIssue(
                code="unsupported_contract_type",
                field=field_name,
                message=(
                    f"Tipo de contrato no soportado para '{field_name}': {expected_type}."
                ),
            )
        )
        return issues

    @staticmethod
    def _load_contract(contract_path: Path) -> dict[str, Any]:
        if not contract_path.exists():
            raise FileNotFoundError(f"No existe el contrato: {contract_path}")

        with contract_path.open("r", encoding="utf-8") as f:
            contract = json.load(f)

        required_top_keys = {"contract_name", "entity", "fields", "required_fields"}
        missing = required_top_keys - set(contract.keys())
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(
                f"El contrato '{contract_path}' no contiene claves obligatorias: {missing_str}"
            )

        return contract
