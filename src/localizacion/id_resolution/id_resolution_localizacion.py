from __future__ import annotations

import sqlite3
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class IDResolutionIssue:
    code: str
    message: str
    field: str | None = None
    severity: str = "error"


@dataclass(slots=True)
class IDResolutionRowResult:
    row_index: int
    is_valid: bool
    resolved_record: dict[str, Any] | None = None
    errors: list[IDResolutionIssue] = field(default_factory=list)
    warnings: list[IDResolutionIssue] = field(default_factory=list)


@dataclass(slots=True)
class IDResolutionBatchResult:
    entity: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    results: list[IDResolutionRowResult]

    @property
    def is_valid_batch(self) -> bool:
        return self.invalid_rows == 0


class IDResolutionLocalizacion:
    """
    Resolución de identidad persistible para:
    - T_Paises
    - T_Subdivisiones_Administrativas
    - T_Localidades
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path else None

    def resolve_rows(self, rows: list[dict[str, Any]]) -> IDResolutionBatchResult:
        entity = self._detect_entity(rows)

        if entity == "T_Paises":
            return self._resolve_countries(rows)

        if entity == "T_Subdivisiones_Administrativas":
            if self.db_path is None:
                raise ValueError(
                    "db_path es obligatorio para resolver subdivisiones administrativas."
                )
            return self._resolve_subdivisions(rows)

        if entity == "T_Localidades":
            if self.db_path is None:
                raise ValueError(
                    "db_path es obligatorio para resolver localidades."
                )
            return self._resolve_localidades(rows)

        return IDResolutionBatchResult(
            entity="UNKNOWN",
            total_rows=len(rows),
            valid_rows=0,
            invalid_rows=len(rows),
            results=[
                IDResolutionRowResult(
                    row_index=row.get("source_row_index", idx),
                    is_valid=False,
                    errors=[
                        IDResolutionIssue(
                            code="unknown_payload_shape",
                            message="No se pudo detectar el tipo de payload territorial.",
                        )
                    ],
                )
                for idx, row in enumerate(rows, start=1)
            ],
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

    def _resolve_countries(self, rows: list[dict[str, Any]]) -> IDResolutionBatchResult:
        results: list[IDResolutionRowResult] = []

        for idx, row in enumerate(rows, start=1):
            row_index = row.get("source_row_index", idx)
            errors: list[IDResolutionIssue] = []

            country_name = row.get("country_name")
            country_iso2 = row.get("country_iso2")
            country_iso3 = row.get("country_iso3")
            semantic_key = row.get("semantic_key")

            if not isinstance(country_iso2, str) or country_iso2.strip() == "":
                errors.append(
                    IDResolutionIssue(
                        code="missing_country_iso2",
                        field="country_iso2",
                        message="country_iso2 es obligatorio para resolver country_id.",
                    )
                )

            if not isinstance(country_name, str) or country_name.strip() == "":
                errors.append(
                    IDResolutionIssue(
                        code="missing_country_name",
                        field="country_name",
                        message="country_name es obligatorio para persistencia.",
                    )
                )

            if not isinstance(country_iso3, str) or country_iso3.strip() == "":
                errors.append(
                    IDResolutionIssue(
                        code="missing_country_iso3",
                        field="country_iso3",
                        message="country_iso3 es obligatorio para persistencia.",
                    )
                )

            if not isinstance(semantic_key, str) or semantic_key.strip() == "":
                errors.append(
                    IDResolutionIssue(
                        code="missing_semantic_key",
                        field="semantic_key",
                        message="semantic_key es obligatorio para persistencia.",
                    )
                )

            if errors:
                results.append(
                    IDResolutionRowResult(
                        row_index=row_index,
                        is_valid=False,
                        resolved_record=None,
                        errors=errors,
                    )
                )
                continue

            country_id = f"country__{country_iso2.lower()}"

            results.append(
                IDResolutionRowResult(
                    row_index=row_index,
                    is_valid=True,
                    resolved_record={
                        "country_id": country_id,
                        "country_name": country_name,
                        "country_name_en": row.get("country_name_en"),
                        "country_name_fr": row.get("country_name_fr"),
                        "country_name_cat": row.get("country_name_cat"),
                        "country_iso2": country_iso2,
                        "country_iso3": country_iso3,
                        "region_global": row.get("region_global"),
                        "semantic_key": semantic_key,
                        "source_file": row.get("source_file"),
                        "source_row_index": row.get("source_row_index"),
                        "raw_payload": row.get("raw_payload"),
                    },
                    errors=[],
                )
            )

        return self._build_batch_result("T_Paises", results)

    def _resolve_subdivisions(self, rows: list[dict[str, Any]]) -> IDResolutionBatchResult:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        results: list[IDResolutionRowResult] = []

        try:
            country_map = self._load_country_map(conn)

            level_1_rows = [r for r in rows if r.get("level") == 1]
            level_2_rows = [r for r in rows if r.get("level") == 2]

            resolved_level_1_by_semantic_key: dict[str, str] = {}

            for idx, row in enumerate(level_1_rows, start=1):
                row_index = row.get("source_row_index", idx)
                result = self._resolve_subdivision_level_1(
                    row=row,
                    row_index=row_index,
                    country_map=country_map,
                )
                results.append(result)

                if result.is_valid and result.resolved_record is not None:
                    resolved_level_1_by_semantic_key[
                        result.resolved_record["semantic_key"]
                    ] = result.resolved_record["subdivision_id"]

            for idx, row in enumerate(level_2_rows, start=1):
                row_index = row.get("source_row_index", idx)
                result = self._resolve_subdivision_level_2(
                    row=row,
                    row_index=row_index,
                    country_map=country_map,
                    resolved_level_1_by_semantic_key=resolved_level_1_by_semantic_key,
                )
                results.append(result)

        finally:
            conn.close()

        results.sort(key=lambda r: r.row_index)
        return self._build_batch_result("T_Subdivisiones_Administrativas", results)

    def _resolve_subdivision_level_1(
        self,
        row: dict[str, Any],
        row_index: int,
        country_map: dict[str, str],
    ) -> IDResolutionRowResult:
        errors: list[IDResolutionIssue] = []

        country_iso2 = row.get("country_iso2")
        subdivision_name = row.get("subdivision_name")
        subdivision_type = row.get("subdivision_type")
        level = row.get("level")
        subdivision_code = row.get("subdivision_code")
        semantic_key = row.get("semantic_key")

        if country_iso2 not in country_map:
            errors.append(
                IDResolutionIssue(
                    code="country_not_found",
                    field="country_iso2",
                    message=f"No existe country_iso2='{country_iso2}' en T_Paises.",
                )
            )

        if level != 1:
            errors.append(
                IDResolutionIssue(
                    code="invalid_level_for_level_1_resolution",
                    field="level",
                    message="Se esperaba una subdivisión de nivel 1.",
                )
            )

        if row.get("parent_semantic_key") is not None:
            errors.append(
                IDResolutionIssue(
                    code="unexpected_parent_semantic_key",
                    field="parent_semantic_key",
                    message="Las subdivisiones de nivel 1 no deben tener parent_semantic_key.",
                )
            )

        if errors:
            return IDResolutionRowResult(
                row_index=row_index,
                is_valid=False,
                resolved_record=None,
                errors=errors,
            )

        pais_id = country_map[country_iso2]
        subdivision_id = self._build_subdivision_id(
            country_iso2=country_iso2,
            level=1,
            subdivision_name=subdivision_name,
            parent_id=None,
        )

        return IDResolutionRowResult(
            row_index=row_index,
            is_valid=True,
            resolved_record={
                "subdivision_id": subdivision_id,
                "nombre": subdivision_name,
                "tipo_subdivision": subdivision_type,
                "nivel": level,
                "pais_id": pais_id,
                "parent_id": None,
                "codigo_subdivision": subdivision_code,
                "source_name": row.get("source_name"),
                "semantic_key": semantic_key,
                "parent_semantic_key": None,
                "country_iso2": country_iso2,
                "source_file": row.get("source_file"),
                "source_row_index": row.get("source_row_index"),
                "raw_payload": row.get("raw_payload"),
            },
            errors=[],
        )

    def _resolve_subdivision_level_2(
        self,
        row: dict[str, Any],
        row_index: int,
        country_map: dict[str, str],
        resolved_level_1_by_semantic_key: dict[str, str],
    ) -> IDResolutionRowResult:
        errors: list[IDResolutionIssue] = []

        country_iso2 = row.get("country_iso2")
        subdivision_name = row.get("subdivision_name")
        subdivision_type = row.get("subdivision_type")
        level = row.get("level")
        subdivision_code = row.get("subdivision_code")
        semantic_key = row.get("semantic_key")
        parent_semantic_key = row.get("parent_semantic_key")

        if country_iso2 not in country_map:
            errors.append(
                IDResolutionIssue(
                    code="country_not_found",
                    field="country_iso2",
                    message=f"No existe country_iso2='{country_iso2}' en T_Paises.",
                )
            )

        if level != 2:
            errors.append(
                IDResolutionIssue(
                    code="invalid_level_for_level_2_resolution",
                    field="level",
                    message="Se esperaba una subdivisión de nivel 2.",
                )
            )

        if not isinstance(parent_semantic_key, str) or parent_semantic_key.strip() == "":
            errors.append(
                IDResolutionIssue(
                    code="missing_parent_semantic_key",
                    field="parent_semantic_key",
                    message="Las subdivisiones de nivel 2 deben tener parent_semantic_key.",
                )
            )
        elif parent_semantic_key not in resolved_level_1_by_semantic_key:
            errors.append(
                IDResolutionIssue(
                    code="parent_not_resolved",
                    field="parent_semantic_key",
                    message=(
                        f"No se pudo resolver el padre con semantic_key='{parent_semantic_key}'."
                    ),
                )
            )

        if errors:
            return IDResolutionRowResult(
                row_index=row_index,
                is_valid=False,
                resolved_record=None,
                errors=errors,
            )

        pais_id = country_map[country_iso2]
        parent_id = resolved_level_1_by_semantic_key[parent_semantic_key]
        subdivision_id = self._build_subdivision_id(
            country_iso2=country_iso2,
            level=2,
            subdivision_name=subdivision_name,
            parent_id=parent_id,
        )

        return IDResolutionRowResult(
            row_index=row_index,
            is_valid=True,
            resolved_record={
                "subdivision_id": subdivision_id,
                "nombre": subdivision_name,
                "tipo_subdivision": subdivision_type,
                "nivel": level,
                "pais_id": pais_id,
                "parent_id": parent_id,
                "codigo_subdivision": subdivision_code,
                "source_name": row.get("source_name"),
                "semantic_key": semantic_key,
                "parent_semantic_key": parent_semantic_key,
                "country_iso2": country_iso2,
                "source_file": row.get("source_file"),
                "source_row_index": row.get("source_row_index"),
                "raw_payload": row.get("raw_payload"),
            },
            errors=[],
        )

    def _resolve_localidades(self, rows: list[dict[str, Any]]) -> IDResolutionBatchResult:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        results: list[IDResolutionRowResult] = []

        try:
            country_map = self._load_country_map(conn)
            province_map = self._load_province_subdivision_map(conn)

            for idx, row in enumerate(rows, start=1):
                row_index = row.get("source_row_index", idx)
                result = self._resolve_localidad_row(
                    row=row,
                    row_index=row_index,
                    country_map=country_map,
                    province_map=province_map,
                )
                results.append(result)

        finally:
            conn.close()

        return self._build_batch_result("T_Localidades", results)

    def _resolve_localidad_row(
        self,
        row: dict[str, Any],
        row_index: int,
        country_map: dict[str, str],
        province_map: dict[str, str],
    ) -> IDResolutionRowResult:
        errors: list[IDResolutionIssue] = []

        country_iso2 = row.get("country_iso2")
        province_code = row.get("province_code")
        subdivision_code = row.get("subdivision_code")
        locality_code = row.get("locality_code")
        locality_name = row.get("locality_name")
        locality_type = row.get("locality_type")
        semantic_key = row.get("semantic_key")

        if country_iso2 not in country_map:
            errors.append(
                IDResolutionIssue(
                    code="country_not_found",
                    field="country_iso2",
                    message=f"No existe country_iso2='{country_iso2}' en T_Paises.",
                )
            )

        if not isinstance(subdivision_code, str) or subdivision_code.strip() == "":
            errors.append(
                IDResolutionIssue(
                    code="missing_subdivision_code",
                    field="subdivision_code",
                    message="subdivision_code es obligatorio para resolver subdivision_id.",
                )
            )
        elif subdivision_code not in province_map:
            errors.append(
                IDResolutionIssue(
                    code="subdivision_not_found",
                    field="subdivision_code",
                    message=(
                        f"No existe una subdivisión de provincia cargada con "
                        f"codigo_subdivision='{subdivision_code}'."
                    ),
                )
            )

        required_strings = {
            "province_code": province_code,
            "locality_code": locality_code,
            "locality_name": locality_name,
            "locality_type": locality_type,
            "semantic_key": semantic_key,
        }
        for field_name, value in required_strings.items():
            if not isinstance(value, str) or value.strip() == "":
                errors.append(
                    IDResolutionIssue(
                        code=f"missing_{field_name}",
                        field=field_name,
                        message=f"{field_name} es obligatorio para persistencia.",
                    )
                )

        if errors:
            return IDResolutionRowResult(
                row_index=row_index,
                is_valid=False,
                resolved_record=None,
                errors=errors,
            )

        pais_id = country_map[country_iso2]
        subdivision_id = province_map[subdivision_code]
        localidad_id = self._build_localidad_id(country_iso2, locality_code)

        return IDResolutionRowResult(
            row_index=row_index,
            is_valid=True,
            resolved_record={
                "localidad_id": localidad_id,
                "nombre": locality_name,
                "tipo_localidad": locality_type,
                "pais_id": pais_id,
                "subdivision_id": subdivision_id,
                "codigo_localidad": locality_code,
                "source_name": row.get("source_name"),
                "latitud": row.get("latitud"),
                "longitud": row.get("longitud"),
                "codigo_postal": row.get("codigo_postal"),
                "population": row.get("population"),
                "semantic_key": semantic_key,
                "country_iso2": country_iso2,
                "province_code": province_code,
                "subdivision_code": subdivision_code,
                "source_file": row.get("source_file"),
                "source_row_index": row.get("source_row_index"),
                "raw_payload": row.get("raw_payload"),
            },
            errors=[],
        )

    def _load_country_map(self, conn: sqlite3.Connection) -> dict[str, str]:
        rows = conn.execute(
            """
            SELECT id, codigo_iso
            FROM T_Paises
            """
        ).fetchall()
        return {row["codigo_iso"]: row["id"] for row in rows}

    def _load_province_subdivision_map(self, conn: sqlite3.Connection) -> dict[str, str]:
        rows = conn.execute(
            """
            SELECT id, codigo_subdivision
            FROM T_Subdivisiones_Administrativas
            WHERE nivel = 2
            """
        ).fetchall()

        province_map: dict[str, str] = {}

        for row in rows:
            raw_code = row["codigo_subdivision"]
            if raw_code is None:
                continue

            code = str(raw_code).strip()
            if code == "":
                continue

            if code.isdigit():
                code = code.zfill(2)

            province_map[code] = row["id"]

        return province_map

    @staticmethod
    def _slugify(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        ascii_only = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        ascii_only = ascii_only.lower()
        cleaned = []
        for ch in ascii_only:
            if ch.isalnum():
                cleaned.append(ch)
            else:
                cleaned.append("_")
        slug = "".join(cleaned)
        while "__" in slug:
            slug = slug.replace("__", "_")
        return slug.strip("_")

    def _build_subdivision_id(
        self,
        country_iso2: str,
        level: int,
        subdivision_name: str,
        parent_id: str | None,
    ) -> str:
        name_slug = self._slugify(subdivision_name)

        if level == 1:
            return f"subdivision__{country_iso2.lower()}__1__{name_slug}"

        parent_slug = self._slugify(parent_id or "root")
        return f"subdivision__{country_iso2.lower()}__2__{name_slug}__{parent_slug}"

    @staticmethod
    def _build_localidad_id(country_iso2: str, locality_code: str) -> str:
        return f"localidad__{country_iso2.lower()}__{locality_code}"

    @staticmethod
    def _build_batch_result(
        entity: str,
        results: list[IDResolutionRowResult],
    ) -> IDResolutionBatchResult:
        valid_rows = sum(1 for r in results if r.is_valid)
        invalid_rows = len(results) - valid_rows

        return IDResolutionBatchResult(
            entity=entity,
            total_rows=len(results),
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            results=results,
        )