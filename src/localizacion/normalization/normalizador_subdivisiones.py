from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class NormalizationIssue:
    code: str
    message: str
    field: str | None = None


@dataclass(slots=True)
class NormalizedSubdivisionRecord:
    country_iso2: str
    subdivision_name: str
    subdivision_type: str
    level: int
    subdivision_code: str | None
    parent_semantic_key: str | None
    semantic_key: str
    source_name: str
    source_row_index: int | None
    source_file: str | None
    raw_payload: dict[str, Any]


@dataclass(slots=True)
class NormalizationExplodedRowResult:
    row_index: int
    is_valid: bool
    normalized_records: list[NormalizedSubdivisionRecord] = field(default_factory=list)
    errors: list[NormalizationIssue] = field(default_factory=list)


@dataclass(slots=True)
class NormalizationBatchResult:
    entity: str
    total_source_rows: int
    valid_source_rows: int
    invalid_source_rows: int
    exploded_records_count: int
    results: list[NormalizationExplodedRowResult]

    @property
    def is_valid_batch(self) -> bool:
        return self.invalid_source_rows == 0


class NormalizadorSubdivisiones:
    """
    Normalización territorial para subdivisiones administrativas desde fuente España.

    Una fila fuente genera múltiples registros normalizados:
    - nivel 1: comunidad autónoma
    - nivel 2: provincia
    """

    entity = "T_Subdivisiones_Administrativas"
    country_iso2 = "ES"

    def normalize_rows(self, rows: list[dict[str, Any]]) -> NormalizationBatchResult:
        results: list[NormalizationExplodedRowResult] = []

        for idx, row in enumerate(rows, start=1):
            row_index = row.get("_row_index", idx)
            result = self.normalize_row(row=row, row_index=row_index)
            results.append(result)

        valid_source_rows = sum(1 for r in results if r.is_valid)
        invalid_source_rows = len(results) - valid_source_rows
        exploded_records_count = sum(len(r.normalized_records) for r in results if r.is_valid)

        return NormalizationBatchResult(
            entity=self.entity,
            total_source_rows=len(rows),
            valid_source_rows=valid_source_rows,
            invalid_source_rows=invalid_source_rows,
            exploded_records_count=exploded_records_count,
            results=results,
        )

    def normalize_row(
        self,
        row: dict[str, Any],
        row_index: int,
    ) -> NormalizationExplodedRowResult:
        errors: list[NormalizationIssue] = []

        try:
            ccaa_name = self._normalize_required_string(row.get("CCAA"))
            ccaa_code = self._normalize_optional_code(row.get("Cod_CCAA"), expected_len=2)
            provincia_name = self._normalize_required_string(row.get("Provincia"))
            provincia_code = self._normalize_optional_code(row.get("Codigo"), expected_len=2)

            source_file = row.get("_source_file")
            source_row_index = row.get("_row_index")

            ccaa_semantic_key = self._build_semantic_key_level_1(
                country_iso2=self.country_iso2,
                subdivision_name=ccaa_name,
            )

            provincia_semantic_key = self._build_semantic_key_level_2(
                country_iso2=self.country_iso2,
                subdivision_name=provincia_name,
                parent_semantic_key=ccaa_semantic_key,
            )

            level_1_record = NormalizedSubdivisionRecord(
                country_iso2=self.country_iso2,
                subdivision_name=ccaa_name,
                subdivision_type="comunidad_autonoma",
                level=1,
                subdivision_code=ccaa_code,
                parent_semantic_key=None,
                semantic_key=ccaa_semantic_key,
                source_name=ccaa_name,
                source_row_index=source_row_index,
                source_file=source_file,
                raw_payload=row,
            )

            level_2_record = NormalizedSubdivisionRecord(
                country_iso2=self.country_iso2,
                subdivision_name=provincia_name,
                subdivision_type="provincia",
                level=2,
                subdivision_code=provincia_code,
                parent_semantic_key=ccaa_semantic_key,
                semantic_key=provincia_semantic_key,
                source_name=provincia_name,
                source_row_index=source_row_index,
                source_file=source_file,
                raw_payload=row,
            )

            return NormalizationExplodedRowResult(
                row_index=row_index,
                is_valid=True,
                normalized_records=[level_1_record, level_2_record],
                errors=[],
            )

        except ValueError as exc:
            errors.append(
                NormalizationIssue(
                    code="normalization_error",
                    message=str(exc),
                )
            )
            return NormalizationExplodedRowResult(
                row_index=row_index,
                is_valid=False,
                normalized_records=[],
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
    def _normalize_optional_code(value: Any, expected_len: int | None = None) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(f"Código fuente con tipo no soportado: {type(value).__name__}.")

        normalized = value.strip()

        if normalized == "":
            return None

        if expected_len is not None and normalized.isdigit():
            normalized = normalized.zfill(expected_len)

        return normalized

    @staticmethod
    def _build_semantic_key_level_1(country_iso2: str, subdivision_name: str) -> str:
        return f"{country_iso2}|1|{subdivision_name}"

    @staticmethod
    def _build_semantic_key_level_2(
        country_iso2: str,
        subdivision_name: str,
        parent_semantic_key: str,
    ) -> str:
        return f"{country_iso2}|2|{subdivision_name}|{parent_semantic_key}"
