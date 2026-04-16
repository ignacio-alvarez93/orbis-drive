from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class NormalizationIssue:
    code: str
    message: str
    field: str | None = None


@dataclass(slots=True)
class NormalizedLocalidadRecord:
    country_iso2: str
    province_code: str
    subdivision_code: str
    locality_code: str
    locality_name: str
    locality_type: str
    semantic_key: str
    source_name: str
    source_row_index: int | None
    source_file: str | None
    raw_payload: dict[str, Any]


@dataclass(slots=True)
class NormalizationRowResult:
    row_index: int
    is_valid: bool
    normalized_record: NormalizedLocalidadRecord | None = None
    errors: list[NormalizationIssue] = field(default_factory=list)


@dataclass(slots=True)
class NormalizationBatchResult:
    entity: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    results: list[NormalizationRowResult]

    @property
    def is_valid_batch(self) -> bool:
        return self.invalid_rows == 0


class NormalizadorLocalidades:
    """
    Normalización territorial para localidades desde fuente INE España.

    Input esperado:
    - CPRO
    - CMUN
    - DC
    - NOMBRE

    Output:
    - payload interno de localidad multipaís, listo para DVL.
    """

    entity = "T_Localidades"
    country_iso2 = "ES"
    locality_type = "municipio"

    def normalize_rows(self, rows: list[dict[str, Any]]) -> NormalizationBatchResult:
        results: list[NormalizationRowResult] = []

        for idx, row in enumerate(rows, start=1):
            row_index = row.get("_row_index", idx)
            result = self.normalize_row(row=row, row_index=row_index)
            results.append(result)

        valid_rows = sum(1 for r in results if r.is_valid)
        invalid_rows = len(results) - valid_rows

        return NormalizationBatchResult(
            entity=self.entity,
            total_rows=len(rows),
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            results=results,
        )

    def normalize_row(
        self,
        row: dict[str, Any],
        row_index: int,
    ) -> NormalizationRowResult:
        errors: list[NormalizationIssue] = []

        try:
            province_code = self._normalize_code(row.get("CPRO"), expected_len=2, field_name="CPRO")
            municipality_code = self._normalize_code(row.get("CMUN"), expected_len=3, field_name="CMUN")
            locality_name = self._normalize_required_string(row.get("NOMBRE"), field_name="NOMBRE")

            locality_code = f"{province_code}{municipality_code}"
            semantic_key = self._build_semantic_key(
                country_iso2=self.country_iso2,
                province_code=province_code,
                locality_name=locality_name,
            )

            normalized = NormalizedLocalidadRecord(
                country_iso2=self.country_iso2,
                province_code=province_code,
                subdivision_code=province_code,
                locality_code=locality_code,
                locality_name=locality_name,
                locality_type=self.locality_type,
                semantic_key=semantic_key,
                source_name=locality_name,
                source_row_index=row.get("_row_index"),
                source_file=row.get("_source_file"),
                raw_payload=row,
            )

            return NormalizationRowResult(
                row_index=row_index,
                is_valid=True,
                normalized_record=normalized,
                errors=[],
            )

        except ValueError as exc:
            errors.append(
                NormalizationIssue(
                    code="normalization_error",
                    message=str(exc),
                )
            )
            return NormalizationRowResult(
                row_index=row_index,
                is_valid=False,
                normalized_record=None,
                errors=errors,
            )

    @staticmethod
    def _normalize_required_string(value: Any, field_name: str) -> str:
        if value is None:
            raise ValueError(f"Campo requerido ausente en normalización: {field_name}.")

        if not isinstance(value, str):
            raise ValueError(
                f"Se esperaba string en {field_name} y se recibió {type(value).__name__}."
            )

        normalized = value.strip()
        if normalized == "":
            raise ValueError(f"Campo requerido vacío tras strip(): {field_name}.")

        return normalized

    @staticmethod
    def _normalize_code(value: Any, expected_len: int, field_name: str) -> str:
        if value is None:
            raise ValueError(f"Código requerido ausente en normalización: {field_name}.")

        if not isinstance(value, str):
            raise ValueError(
                f"Se esperaba string en {field_name} y se recibió {type(value).__name__}."
            )

        normalized = value.strip()

        if normalized == "":
            raise ValueError(f"Código vacío tras strip(): {field_name}.")

        if not normalized.isdigit():
            raise ValueError(
                f"{field_name} debe contener solo dígitos y se recibió '{normalized}'."
            )

        normalized = normalized.zfill(expected_len)

        if len(normalized) != expected_len:
            raise ValueError(
                f"{field_name} no pudo normalizarse a longitud {expected_len} y quedó '{normalized}'."
            )

        return normalized

    @staticmethod
    def _build_semantic_key(
        country_iso2: str,
        province_code: str,
        locality_name: str,
    ) -> str:
        return f"{country_iso2}|{province_code}|{locality_name}"