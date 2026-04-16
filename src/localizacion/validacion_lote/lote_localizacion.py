from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class LoteIssue:
    code: str
    message: str
    field: str | None = None
    severity: str = "error"


@dataclass(slots=True)
class LoteRowResult:
    row_index: int
    is_valid: bool
    errors: list[LoteIssue] = field(default_factory=list)
    warnings: list[LoteIssue] = field(default_factory=list)
    validated_record: dict[str, Any] | None = None


@dataclass(slots=True)
class LoteBatchResult:
    entity: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    is_valid_dataset: bool
    results: list[LoteRowResult]
    duplicates_detected: int = 0
    conflicts_detected: int = 0


class LoteLocalizacionValidator:
    """
    Validación global de lote para:
    - T_Paises
    - T_Subdivisiones_Administrativas
    - T_Localidades
    """

    def validate_rows(self, rows: list[dict[str, Any]]) -> LoteBatchResult:
        entity = self._detect_entity(rows)

        if entity == "T_Paises":
            return self._validate_countries(rows)

        if entity == "T_Subdivisiones_Administrativas":
            return self._validate_subdivisions(rows)

        if entity == "T_Localidades":
            return self._validate_localidades(rows)

        return LoteBatchResult(
            entity="UNKNOWN",
            total_rows=len(rows),
            valid_rows=0,
            invalid_rows=len(rows),
            is_valid_dataset=False,
            results=[
                LoteRowResult(
                    row_index=row.get("source_row_index", idx),
                    is_valid=False,
                    errors=[
                        LoteIssue(
                            code="unknown_payload_shape",
                            message="No se pudo detectar el tipo de payload territorial.",
                        )
                    ],
                    validated_record=None,
                )
                for idx, row in enumerate(rows, start=1)
            ],
            duplicates_detected=0,
            conflicts_detected=1 if rows else 0,
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

    def _validate_countries(self, rows: list[dict[str, Any]]) -> LoteBatchResult:
        indexed_results = [
            LoteRowResult(
                row_index=row.get("source_row_index", idx),
                is_valid=True,
                validated_record=row,
            )
            for idx, row in enumerate(rows, start=1)
        ]
        result_by_row_index = {r.row_index: r for r in indexed_results}

        duplicates_detected = 0
        conflicts_detected = 0

        semantic_key_map: dict[str, list[dict[str, Any]]] = {}
        iso2_map: dict[str, list[dict[str, Any]]] = {}
        iso3_map: dict[str, list[dict[str, Any]]] = {}

        for row in rows:
            semantic_key_map.setdefault(row["semantic_key"], []).append(row)
            iso2_map.setdefault(row["country_iso2"], []).append(row)
            iso3_map.setdefault(row["country_iso3"], []).append(row)

        for semantic_key, group in semantic_key_map.items():
            if len(group) <= 1:
                continue

            if self._all_equal(group, ["country_name", "country_iso2", "country_iso3"]):
                duplicates_detected += len(group) - 1
                for row in group:
                    result_by_row_index[row["source_row_index"]].warnings.append(
                        LoteIssue(
                            code="duplicate_semantic_key",
                            field="semantic_key",
                            severity="warning",
                            message=f"Duplicado exacto detectado en semantic_key='{semantic_key}'.",
                        )
                    )
            else:
                conflicts_detected += 1
                for row in group:
                    rr = result_by_row_index[row["source_row_index"]]
                    rr.is_valid = False
                    rr.errors.append(
                        LoteIssue(
                            code="semantic_key_conflict",
                            field="semantic_key",
                            message=(
                                f"Conflicto interno: múltiples registros con semantic_key='{semantic_key}' "
                                "pero contenido semántico distinto."
                            ),
                        )
                    )

        for iso2, group in iso2_map.items():
            if len(group) > 1 and not self._all_equal(group, ["country_name", "country_iso3"]):
                conflicts_detected += 1
                for row in group:
                    rr = result_by_row_index[row["source_row_index"]]
                    rr.is_valid = False
                    rr.errors.append(
                        LoteIssue(
                            code="country_iso2_conflict",
                            field="country_iso2",
                            message=(
                                f"Conflicto interno: country_iso2='{iso2}' aparece asociado a "
                                "nombres o iso3 distintos dentro del lote."
                            ),
                        )
                    )

        for iso3, group in iso3_map.items():
            if len(group) > 1 and not self._all_equal(group, ["country_name", "country_iso2"]):
                conflicts_detected += 1
                for row in group:
                    rr = result_by_row_index[row["source_row_index"]]
                    rr.is_valid = False
                    rr.errors.append(
                        LoteIssue(
                            code="country_iso3_conflict",
                            field="country_iso3",
                            message=(
                                f"Conflicto interno: country_iso3='{iso3}' aparece asociado a "
                                "nombres o iso2 distintos dentro del lote."
                            ),
                        )
                    )

        valid_rows = sum(1 for r in indexed_results if r.is_valid)
        invalid_rows = len(indexed_results) - valid_rows

        return LoteBatchResult(
            entity="T_Paises",
            total_rows=len(indexed_results),
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            is_valid_dataset=(invalid_rows == 0),
            results=indexed_results,
            duplicates_detected=duplicates_detected,
            conflicts_detected=conflicts_detected,
        )

    def _validate_subdivisions(self, rows: list[dict[str, Any]]) -> LoteBatchResult:
        indexed_results = [
            LoteRowResult(
                row_index=row.get("source_row_index", idx),
                is_valid=True,
                validated_record=row,
            )
            for idx, row in enumerate(rows, start=1)
        ]
        result_by_row_index = {r.row_index: r for r in indexed_results}

        duplicates_detected = 0
        conflicts_detected = 0

        semantic_key_map: dict[str, list[dict[str, Any]]] = {}
        parent_key_set: set[str] = set()

        for row in rows:
            semantic_key = row["semantic_key"]
            semantic_key_map.setdefault(semantic_key, []).append(row)

            if row.get("level") == 1:
                parent_key_set.add(semantic_key)

        for semantic_key, group in semantic_key_map.items():
            if len(group) <= 1:
                continue

            if self._all_equal(
                group,
                ["country_iso2", "subdivision_name", "subdivision_type", "level", "parent_semantic_key"],
            ):
                duplicates_detected += len(group) - 1
                for row in group:
                    result_by_row_index[row["source_row_index"]].warnings.append(
                        LoteIssue(
                            code="duplicate_semantic_key",
                            field="semantic_key",
                            severity="warning",
                            message=f"Duplicado exacto detectado en semantic_key='{semantic_key}'.",
                        )
                    )
            else:
                conflicts_detected += 1
                for row in group:
                    rr = result_by_row_index[row["source_row_index"]]
                    rr.is_valid = False
                    rr.errors.append(
                        LoteIssue(
                            code="semantic_key_conflict",
                            field="semantic_key",
                            message=(
                                f"Conflicto interno: múltiples registros con semantic_key='{semantic_key}' "
                                "pero contenido semántico distinto."
                            ),
                        )
                    )

        for row in rows:
            if row.get("level") == 2:
                parent_semantic_key = row.get("parent_semantic_key")
                if parent_semantic_key not in parent_key_set:
                    conflicts_detected += 1
                    rr = result_by_row_index[row["source_row_index"]]
                    rr.is_valid = False
                    rr.errors.append(
                        LoteIssue(
                            code="missing_parent_in_batch",
                            field="parent_semantic_key",
                            message=(
                                f"parent_semantic_key='{parent_semantic_key}' no existe "
                                "como subdivisión de nivel 1 dentro del lote."
                            ),
                        )
                    )

        valid_rows = sum(1 for r in indexed_results if r.is_valid)
        invalid_rows = len(indexed_results) - valid_rows

        return LoteBatchResult(
            entity="T_Subdivisiones_Administrativas",
            total_rows=len(indexed_results),
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            is_valid_dataset=(invalid_rows == 0),
            results=indexed_results,
            duplicates_detected=duplicates_detected,
            conflicts_detected=conflicts_detected,
        )

    def _validate_localidades(self, rows: list[dict[str, Any]]) -> LoteBatchResult:
        indexed_results = [
            LoteRowResult(
                row_index=row.get("source_row_index", idx),
                is_valid=True,
                validated_record=row,
            )
            for idx, row in enumerate(rows, start=1)
        ]
        result_by_row_index = {r.row_index: r for r in indexed_results}

        duplicates_detected = 0
        conflicts_detected = 0

        locality_code_map: dict[str, list[dict[str, Any]]] = {}
        semantic_key_map: dict[str, list[dict[str, Any]]] = {}

        for row in rows:
            locality_code_map.setdefault(row["locality_code"], []).append(row)
            semantic_key_map.setdefault(row["semantic_key"], []).append(row)

        # 1) Conflictos / duplicados por locality_code
        for locality_code, group in locality_code_map.items():
            if len(group) <= 1:
                continue

            if self._all_equal(
                group,
                ["country_iso2", "province_code", "subdivision_code", "locality_name", "locality_type"],
            ):
                duplicates_detected += len(group) - 1
                for row in group:
                    result_by_row_index[row["source_row_index"]].warnings.append(
                        LoteIssue(
                            code="duplicate_locality_code",
                            field="locality_code",
                            severity="warning",
                            message=f"Duplicado exacto detectado en locality_code='{locality_code}'.",
                        )
                    )
            else:
                conflicts_detected += 1
                for row in group:
                    rr = result_by_row_index[row["source_row_index"]]
                    rr.is_valid = False
                    rr.errors.append(
                        LoteIssue(
                            code="locality_code_conflict",
                            field="locality_code",
                            message=(
                                f"Conflicto interno: locality_code='{locality_code}' aparece asociado "
                                "a contenido semántico distinto."
                            ),
                        )
                    )

        # 2) Conflictos / duplicados por semantic_key
        for semantic_key, group in semantic_key_map.items():
            if len(group) <= 1:
                continue

            if self._all_equal(
                group,
                ["country_iso2", "province_code", "subdivision_code", "locality_code", "locality_name", "locality_type"],
            ):
                duplicates_detected += len(group) - 1
                for row in group:
                    result_by_row_index[row["source_row_index"]].warnings.append(
                        LoteIssue(
                            code="duplicate_semantic_key",
                            field="semantic_key",
                            severity="warning",
                            message=f"Duplicado exacto detectado en semantic_key='{semantic_key}'.",
                        )
                    )
            else:
                conflicts_detected += 1
                for row in group:
                    rr = result_by_row_index[row["source_row_index"]]
                    rr.is_valid = False
                    rr.errors.append(
                        LoteIssue(
                            code="semantic_key_conflict",
                            field="semantic_key",
                            message=(
                                f"Conflicto interno: semantic_key='{semantic_key}' aparece asociado "
                                "a locality_code o contenido distinto."
                            ),
                        )
                    )

        valid_rows = sum(1 for r in indexed_results if r.is_valid)
        invalid_rows = len(indexed_results) - valid_rows

        return LoteBatchResult(
            entity="T_Localidades",
            total_rows=len(indexed_results),
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            is_valid_dataset=(invalid_rows == 0),
            results=indexed_results,
            duplicates_detected=duplicates_detected,
            conflicts_detected=conflicts_detected,
        )

    @staticmethod
    def _all_equal(group: list[dict[str, Any]], keys: list[str]) -> bool:
        if not group:
            return True

        first = group[0]
        first_signature = tuple(first.get(k) for k in keys)

        for item in group[1:]:
            signature = tuple(item.get(k) for k in keys)
            if signature != first_signature:
                return False

        return True