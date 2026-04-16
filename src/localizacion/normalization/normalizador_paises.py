from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class NormalizationIssue:
    code: str
    message: str
    field: str | None = None


@dataclass(slots=True)
class NormalizedCountryRecord:
    country_name: str
    country_name_en: str | None
    country_name_fr: str | None
    country_name_cat: str | None
    country_iso2: str
    country_iso3: str
    region_global: str | None
    semantic_key: str
    source_file: str | None
    source_row_index: int | None
    raw_payload: dict[str, Any]


@dataclass(slots=True)
class NormalizationRowResult:
    row_index: int
    is_valid: bool
    normalized_record: NormalizedCountryRecord | None = None
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


class NormalizadorPaises:
    """
    Capa de normalización territorial para T_Paises.

    Permitido:
    - strip de strings
    - uppercase de ISO
    - empty string -> None en opcionales
    - construcción del payload interno estable
    - generación de semantic_key

    Prohibido:
    - inferir datos ausentes
    - inventar alias
    - corregir geopolítica
    """

    entity = "T_Paises"

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
            country_name = self._normalize_required_string(row.get("es"))
            country_iso2 = self._normalize_required_iso(row.get("iso2"), expected_len=2)
            country_iso3 = self._normalize_required_iso(row.get("iso3"), expected_len=3)

            country_name_en = self._normalize_optional_string(row.get("en"))
            country_name_fr = self._normalize_optional_string(row.get("fr"))
            country_name_cat = self._normalize_optional_string(row.get("cat"))
            region_global = self._normalize_optional_string(row.get("region_global"))

            normalized = NormalizedCountryRecord(
                country_name=country_name,
                country_name_en=country_name_en,
                country_name_fr=country_name_fr,
                country_name_cat=country_name_cat,
                country_iso2=country_iso2,
                country_iso3=country_iso3,
                region_global=region_global,
                semantic_key=country_iso2,
                source_file=row.get("_source_file"),
                source_row_index=row.get("_row_index"),
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
    def _normalize_required_string(value: Any) -> str:
        if value is None:
            raise ValueError("Campo requerido ausente en normalización.")

        if not isinstance(value, str):
            raise ValueError(f"Se esperaba string y se recibió {type(value).__name__}.")

        normalized = value.strip()
        if normalized == "":
            raise ValueError("Campo requerido vacío tras strip().")

        return normalized

    @staticmethod
    def _normalize_optional_string(value: Any) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(
                f"Campo opcional con tipo no soportado: {type(value).__name__}."
            )

        normalized = value.strip()
        return normalized if normalized != "" else None

    @staticmethod
    def _normalize_required_iso(value: Any, expected_len: int) -> str:
        if value is None:
            raise ValueError("Código ISO requerido ausente en normalización.")

        if not isinstance(value, str):
            raise ValueError(
                f"Código ISO debe ser string y se recibió {type(value).__name__}."
            )

        normalized = value.strip().upper()

        if len(normalized) != expected_len:
            raise ValueError(
                f"Código ISO normalizado con longitud inválida: '{normalized}'."
            )

        if not normalized.isalpha():
            raise ValueError(
                f"Código ISO normalizado contiene caracteres no alfabéticos: '{normalized}'."
            )

        return normalized