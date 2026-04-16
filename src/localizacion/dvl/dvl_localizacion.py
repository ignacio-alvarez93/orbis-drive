from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


ISO2_PATTERN = re.compile(r"^[A-Z]{2}$")
ISO3_PATTERN = re.compile(r"^[A-Z]{3}$")
CODE2_PATTERN = re.compile(r"^\d{2}$")
CODE5_PATTERN = re.compile(r"^\d{5}$")


@dataclass(slots=True)
class DVLIssue:
    code: str
    message: str
    field: str | None = None
    severity: str = "error"


@dataclass(slots=True)
class DVLRowResult:
    row_index: int
    is_valid: bool
    errors: list[DVLIssue] = field(default_factory=list)
    warnings: list[DVLIssue] = field(default_factory=list)
    validated_record: dict[str, Any] | None = None


@dataclass(slots=True)
class DVLBatchResult:
    entity: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    results: list[DVLRowResult]

    @property
    def is_valid_batch(self) -> bool:
        return self.invalid_rows == 0


class DVLLocalizacion:
    """
    Validación semántica territorial.
    Soporta:
    - T_Paises
    - T_Subdivisiones_Administrativas
    - T_Localidades
    """

    def validate_rows(self, rows: list[dict[str, Any]]) -> DVLBatchResult:
        results: list[DVLRowResult] = []
        detected_entity = self._detect_entity(rows)

        for idx, row in enumerate(rows, start=1):
            row_index = row.get("source_row_index", idx)

            if detected_entity == "T_Paises":
                result = self._validate_country_row(row=row, row_index=row_index)
            elif detected_entity == "T_Subdivisiones_Administrativas":
                result = self._validate_subdivision_row(row=row, row_index=row_index)
            elif detected_entity == "T_Localidades":
                result = self._validate_localidad_row(row=row, row_index=row_index)
            else:
                result = DVLRowResult(
                    row_index=row_index,
                    is_valid=False,
                    errors=[
                        DVLIssue(
                            code="unknown_payload_shape",
                            message="No se pudo detectar el tipo de payload territorial.",
                        )
                    ],
                    validated_record=None,
                )

            results.append(result)

        valid_rows = sum(1 for r in results if r.is_valid)
        invalid_rows = len(results) - valid_rows

        return DVLBatchResult(
            entity=detected_entity,
            total_rows=len(rows),
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            results=results,
        )

    def _detect_entity(self, rows: list[dict[str, Any]]) -> str:
        if not rows:
            return "UNKNOWN"

        sample = rows[0]

        if "country_name" in sample and "country_iso3" in sample:
            return "T_Paises"

        if "subdivision_name" in sample and "subdivision_type" in sample:
            return "T_Subdivisiones_Administrativas"

        if "locality_name" in sample and "locality_code" in sample:
            return "T_Localidades"

        return "UNKNOWN"

    def _validate_country_row(self, row: dict[str, Any], row_index: int) -> DVLRowResult:
        errors: list[DVLIssue] = []
        warnings: list[DVLIssue] = []

        country_name = row.get("country_name")
        country_iso2 = row.get("country_iso2")
        country_iso3 = row.get("country_iso3")
        semantic_key = row.get("semantic_key")
        source_row_index = row.get("source_row_index")
        raw_payload = row.get("raw_payload")

        if not isinstance(country_name, str) or country_name.strip() == "":
            errors.append(
                DVLIssue(
                    code="invalid_country_name",
                    field="country_name",
                    message="country_name debe ser string no vacío.",
                )
            )

        if not isinstance(country_iso2, str) or ISO2_PATTERN.fullmatch(country_iso2) is None:
            errors.append(
                DVLIssue(
                    code="invalid_country_iso2",
                    field="country_iso2",
                    message="country_iso2 debe tener exactamente 2 letras mayúsculas.",
                )
            )

        if not isinstance(country_iso3, str) or ISO3_PATTERN.fullmatch(country_iso3) is None:
            errors.append(
                DVLIssue(
                    code="invalid_country_iso3",
                    field="country_iso3",
                    message="country_iso3 debe tener exactamente 3 letras mayúsculas.",
                )
            )

        if not isinstance(semantic_key, str) or semantic_key.strip() == "":
            errors.append(
                DVLIssue(
                    code="missing_semantic_key",
                    field="semantic_key",
                    message="semantic_key es obligatorio en el payload normalizado.",
                )
            )
        elif isinstance(country_iso2, str) and semantic_key != country_iso2:
            errors.append(
                DVLIssue(
                    code="semantic_key_mismatch",
                    field="semantic_key",
                    message="semantic_key debe coincidir exactamente con country_iso2.",
                )
            )

        if not isinstance(source_row_index, int) or source_row_index <= 0:
            errors.append(
                DVLIssue(
                    code="invalid_source_row_index",
                    field="source_row_index",
                    message="source_row_index debe ser un entero positivo.",
                )
            )

        if not isinstance(raw_payload, dict) or not raw_payload:
            errors.append(
                DVLIssue(
                    code="missing_raw_payload",
                    field="raw_payload",
                    message="raw_payload debe existir y contener el dato fuente.",
                )
            )

        for alt_name_field in ("country_name_en", "country_name_fr", "country_name_cat"):
            value = row.get(alt_name_field)
            if value is None:
                warnings.append(
                    DVLIssue(
                        code="missing_optional_alt_name",
                        field=alt_name_field,
                        severity="warning",
                        message=f"{alt_name_field} no está informado.",
                    )
                )

        return DVLRowResult(
            row_index=row_index,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_record=row if len(errors) == 0 else None,
        )

    def _validate_subdivision_row(self, row: dict[str, Any], row_index: int) -> DVLRowResult:
        errors: list[DVLIssue] = []
        warnings: list[DVLIssue] = []

        country_iso2 = row.get("country_iso2")
        subdivision_name = row.get("subdivision_name")
        subdivision_type = row.get("subdivision_type")
        level = row.get("level")
        subdivision_code = row.get("subdivision_code")
        parent_semantic_key = row.get("parent_semantic_key")
        semantic_key = row.get("semantic_key")
        source_row_index = row.get("source_row_index")
        raw_payload = row.get("raw_payload")

        if not isinstance(country_iso2, str) or ISO2_PATTERN.fullmatch(country_iso2) is None:
            errors.append(
                DVLIssue(
                    code="invalid_country_iso2",
                    field="country_iso2",
                    message="country_iso2 debe tener exactamente 2 letras mayúsculas.",
                )
            )

        if not isinstance(subdivision_name, str) or subdivision_name.strip() == "":
            errors.append(
                DVLIssue(
                    code="invalid_subdivision_name",
                    field="subdivision_name",
                    message="subdivision_name debe ser string no vacío.",
                )
            )

        valid_types = {"comunidad_autonoma", "provincia"}
        if not isinstance(subdivision_type, str) or subdivision_type not in valid_types:
            errors.append(
                DVLIssue(
                    code="invalid_subdivision_type",
                    field="subdivision_type",
                    message="subdivision_type debe ser uno de: comunidad_autonoma, provincia.",
                )
            )

        if not isinstance(level, int) or level not in {1, 2}:
            errors.append(
                DVLIssue(
                    code="invalid_level",
                    field="level",
                    message="level debe ser entero y estar en {1, 2} para esta fase.",
                )
            )

        if isinstance(level, int) and isinstance(subdivision_type, str):
            if level == 1 and subdivision_type != "comunidad_autonoma":
                errors.append(
                    DVLIssue(
                        code="level_type_mismatch",
                        field="subdivision_type",
                        message="Las subdivisiones de nivel 1 deben ser comunidad_autonoma.",
                    )
                )
            if level == 2 and subdivision_type != "provincia":
                errors.append(
                    DVLIssue(
                        code="level_type_mismatch",
                        field="subdivision_type",
                        message="Las subdivisiones de nivel 2 deben ser provincia.",
                    )
                )

        if not isinstance(semantic_key, str) or semantic_key.strip() == "":
            errors.append(
                DVLIssue(
                    code="missing_semantic_key",
                    field="semantic_key",
                    message="semantic_key es obligatorio en subdivisiones normalizadas.",
                )
            )
        else:
            if isinstance(level, int):
                if level == 1 and not semantic_key.startswith(f"{country_iso2}|1|"):
                    errors.append(
                        DVLIssue(
                            code="invalid_semantic_key_format",
                            field="semantic_key",
                            message="La semantic_key de nivel 1 no tiene el formato esperado.",
                        )
                    )
                if level == 2 and not semantic_key.startswith(f"{country_iso2}|2|"):
                    errors.append(
                        DVLIssue(
                            code="invalid_semantic_key_format",
                            field="semantic_key",
                            message="La semantic_key de nivel 2 no tiene el formato esperado.",
                        )
                    )

        if isinstance(level, int):
            if level == 1:
                if parent_semantic_key is not None:
                    errors.append(
                        DVLIssue(
                            code="unexpected_parent_semantic_key",
                            field="parent_semantic_key",
                            message="Las subdivisiones de nivel 1 no deben tener parent_semantic_key.",
                        )
                    )
            elif level == 2:
                if not isinstance(parent_semantic_key, str) or parent_semantic_key.strip() == "":
                    errors.append(
                        DVLIssue(
                            code="missing_parent_semantic_key",
                            field="parent_semantic_key",
                            message="Las subdivisiones de nivel 2 deben tener parent_semantic_key.",
                        )
                    )
                elif not parent_semantic_key.startswith(f"{country_iso2}|1|"):
                    errors.append(
                        DVLIssue(
                            code="invalid_parent_semantic_key_format",
                            field="parent_semantic_key",
                            message="parent_semantic_key debe apuntar a una subdivisión de nivel 1 válida.",
                        )
                    )

        if subdivision_code is None:
            warnings.append(
                DVLIssue(
                    code="missing_subdivision_code",
                    field="subdivision_code",
                    severity="warning",
                    message="subdivision_code no está informado.",
                )
            )

        if not isinstance(source_row_index, int) or source_row_index <= 0:
            errors.append(
                DVLIssue(
                    code="invalid_source_row_index",
                    field="source_row_index",
                    message="source_row_index debe ser un entero positivo.",
                )
            )

        if not isinstance(raw_payload, dict) or not raw_payload:
            errors.append(
                DVLIssue(
                    code="missing_raw_payload",
                    field="raw_payload",
                    message="raw_payload debe existir y contener la fila fuente.",
                )
            )

        return DVLRowResult(
            row_index=row_index,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_record=row if len(errors) == 0 else None,
        )

    def _validate_localidad_row(self, row: dict[str, Any], row_index: int) -> DVLRowResult:
        errors: list[DVLIssue] = []
        warnings: list[DVLIssue] = []

        country_iso2 = row.get("country_iso2")
        province_code = row.get("province_code")
        subdivision_code = row.get("subdivision_code")
        locality_code = row.get("locality_code")
        locality_name = row.get("locality_name")
        locality_type = row.get("locality_type")
        semantic_key = row.get("semantic_key")
        source_row_index = row.get("source_row_index")
        raw_payload = row.get("raw_payload")

        if not isinstance(country_iso2, str) or ISO2_PATTERN.fullmatch(country_iso2) is None:
            errors.append(
                DVLIssue(
                    code="invalid_country_iso2",
                    field="country_iso2",
                    message="country_iso2 debe tener exactamente 2 letras mayúsculas.",
                )
            )

        if not isinstance(province_code, str) or CODE2_PATTERN.fullmatch(province_code) is None:
            errors.append(
                DVLIssue(
                    code="invalid_province_code",
                    field="province_code",
                    message="province_code debe tener exactamente 2 dígitos.",
                )
            )

        if not isinstance(subdivision_code, str) or CODE2_PATTERN.fullmatch(subdivision_code) is None:
            errors.append(
                DVLIssue(
                    code="invalid_subdivision_code",
                    field="subdivision_code",
                    message="subdivision_code debe tener exactamente 2 dígitos.",
                )
            )

        if (
            isinstance(province_code, str)
            and isinstance(subdivision_code, str)
            and province_code != subdivision_code
        ):
            errors.append(
                DVLIssue(
                    code="province_subdivision_mismatch",
                    field="subdivision_code",
                    message="subdivision_code debe coincidir con province_code en esta fase.",
                )
            )

        if not isinstance(locality_code, str) or CODE5_PATTERN.fullmatch(locality_code) is None:
            errors.append(
                DVLIssue(
                    code="invalid_locality_code",
                    field="locality_code",
                    message="locality_code debe tener exactamente 5 dígitos.",
                )
            )
        elif isinstance(province_code, str) and not locality_code.startswith(province_code):
            errors.append(
                DVLIssue(
                    code="locality_code_prefix_mismatch",
                    field="locality_code",
                    message="locality_code debe comenzar por province_code.",
                )
            )

        if not isinstance(locality_name, str) or locality_name.strip() == "":
            errors.append(
                DVLIssue(
                    code="invalid_locality_name",
                    field="locality_name",
                    message="locality_name debe ser string no vacío.",
                )
            )

        if locality_type != "municipio":
            errors.append(
                DVLIssue(
                    code="invalid_locality_type",
                    field="locality_type",
                    message="locality_type debe ser 'municipio' en esta fase.",
                )
            )

        expected_semantic_key = None
        if (
            isinstance(country_iso2, str)
            and isinstance(province_code, str)
            and isinstance(locality_name, str)
            and locality_name.strip() != ""
        ):
            expected_semantic_key = f"{country_iso2}|{province_code}|{locality_name}"

        if not isinstance(semantic_key, str) or semantic_key.strip() == "":
            errors.append(
                DVLIssue(
                    code="missing_semantic_key",
                    field="semantic_key",
                    message="semantic_key es obligatorio en localidades normalizadas.",
                )
            )
        elif expected_semantic_key is not None and semantic_key != expected_semantic_key:
            errors.append(
                DVLIssue(
                    code="semantic_key_mismatch",
                    field="semantic_key",
                    message="semantic_key no coincide con el formato esperado ES|CPRO|NOMBRE.",
                )
            )

        if not isinstance(source_row_index, int) or source_row_index <= 0:
            errors.append(
                DVLIssue(
                    code="invalid_source_row_index",
                    field="source_row_index",
                    message="source_row_index debe ser un entero positivo.",
                )
            )

        if not isinstance(raw_payload, dict) or not raw_payload:
            errors.append(
                DVLIssue(
                    code="missing_raw_payload",
                    field="raw_payload",
                    message="raw_payload debe existir y contener la fila fuente.",
                )
            )

        return DVLRowResult(
            row_index=row_index,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_record=row if len(errors) == 0 else None,
        )