from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class IngestionIssue:
    code: str
    message: str
    field: str | None = None
    severity: str = "error"


@dataclass(slots=True)
class IngestionRowResult:
    row_index: int
    status: str  # inserted | skipped_existing | failed
    entity_id: str | None = None
    errors: list[IngestionIssue] = field(default_factory=list)


@dataclass(slots=True)
class IngestionBatchResult:
    entity: str
    processed: int
    inserted: int
    skipped_existing: int
    failed: int
    results: list[IngestionRowResult]

    @property
    def is_successful(self) -> bool:
        return self.failed == 0


class LocalizacionLoader:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    # -------------------------
    # T_Paises
    # -------------------------
    def ingest_paises(
        self,
        rows: list[dict[str, Any]],
        dry_run: bool = False,
    ) -> IngestionBatchResult:
        results: list[IngestionRowResult] = []
        inserted = 0
        skipped_existing = 0
        failed = 0

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            for row in rows:
                row_index = row.get("source_row_index", 0)
                result = self._ingest_pais(conn=conn, row=row, dry_run=dry_run)
                result.row_index = row_index
                results.append(result)

                if result.status == "inserted":
                    inserted += 1
                elif result.status == "skipped_existing":
                    skipped_existing += 1
                elif result.status == "failed":
                    failed += 1

            if dry_run:
                conn.rollback()
            else:
                conn.commit()

        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        return IngestionBatchResult(
            entity="T_Paises",
            processed=len(rows),
            inserted=inserted,
            skipped_existing=skipped_existing,
            failed=failed,
            results=results,
        )

    def _ingest_pais(
        self,
        conn: sqlite3.Connection,
        row: dict[str, Any],
        dry_run: bool,
    ) -> IngestionRowResult:
        country_id = row.get("country_id")
        country_name = row.get("country_name")
        country_iso2 = row.get("country_iso2")
        country_iso3 = row.get("country_iso3")
        region_global = row.get("region_global")

        required_fields = {
            "country_id": country_id,
            "country_name": country_name,
            "country_iso2": country_iso2,
            "country_iso3": country_iso3,
        }
        missing = [k for k, v in required_fields.items() if not isinstance(v, str) or v.strip() == ""]
        if missing:
            return IngestionRowResult(
                row_index=0,
                status="failed",
                entity_id=country_id if isinstance(country_id, str) else None,
                errors=[
                    IngestionIssue(
                        code="missing_required_persistible_fields",
                        message=f"Faltan campos obligatorios persistibles: {', '.join(missing)}.",
                    )
                ],
            )

        existing_by_id = conn.execute(
            "SELECT id FROM T_Paises WHERE id = ?",
            (country_id,),
        ).fetchone()
        if existing_by_id is not None:
            return IngestionRowResult(
                row_index=0,
                status="skipped_existing",
                entity_id=country_id,
            )

        existing_by_iso2 = conn.execute(
            "SELECT id FROM T_Paises WHERE codigo_iso = ?",
            (country_iso2,),
        ).fetchone()
        if existing_by_iso2 is not None:
            return IngestionRowResult(
                row_index=0,
                status="failed",
                entity_id=country_id,
                errors=[
                    IngestionIssue(
                        code="country_iso2_conflict_in_db",
                        field="country_iso2",
                        message=(
                            f"Ya existe un país con codigo_iso='{country_iso2}' "
                            f"pero con id='{existing_by_iso2['id']}'."
                        ),
                    )
                ],
            )

        if not dry_run:
            conn.execute(
                """
                INSERT INTO T_Paises (
                    id, nombre, codigo_iso, codigo_iso3, region_global
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (country_id, country_name, country_iso2, country_iso3, region_global),
            )

        return IngestionRowResult(
            row_index=0,
            status="inserted",
            entity_id=country_id,
        )

    # -------------------------
    # T_Subdivisiones_Administrativas
    # -------------------------
    def ingest_subdivisiones(
        self,
        rows: list[dict[str, Any]],
        dry_run: bool = False,
    ) -> IngestionBatchResult:
        results: list[IngestionRowResult] = []
        inserted = 0
        skipped_existing = 0
        failed = 0

        level_1_rows = [r for r in rows if r.get("nivel") == 1]
        level_2_rows = [r for r in rows if r.get("nivel") == 2]
        ordered_rows = level_1_rows + level_2_rows

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            # IDs ya existentes en DB al comenzar
            existing_ids = {
                row["id"]
                for row in conn.execute(
                    "SELECT id FROM T_Subdivisiones_Administrativas"
                ).fetchall()
            }

            available_ids = set(existing_ids)

            for row in ordered_rows:
                row_index = row.get("source_row_index", 0)
                result = self._ingest_subdivision(
                    conn=conn,
                    row=row,
                    dry_run=dry_run,
                    available_ids=available_ids,
                )
                result.row_index = row_index
                results.append(result)

                if result.status == "inserted":
                    inserted += 1
                    if result.entity_id:
                        available_ids.add(result.entity_id)
                elif result.status == "skipped_existing":
                    skipped_existing += 1
                    if result.entity_id:
                        available_ids.add(result.entity_id)
                elif result.status == "failed":
                    failed += 1

            if dry_run:
                conn.rollback()
            else:
                conn.commit()

        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        return IngestionBatchResult(
            entity="T_Subdivisiones_Administrativas",
            processed=len(ordered_rows),
            inserted=inserted,
            skipped_existing=skipped_existing,
            failed=failed,
            results=results,
        )

        # -------------------------
    # T_Localidades
    # -------------------------
    def ingest_localidades(
        self,
        rows: list[dict[str, Any]],
        dry_run: bool = False,
    ) -> IngestionBatchResult:
        results: list[IngestionRowResult] = []
        inserted = 0
        skipped_existing = 0
        failed = 0

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            existing_ids = {
                row["id"]
                for row in conn.execute(
                    "SELECT id FROM T_Localidades"
                ).fetchall()
            }

            available_country_ids = {
                row["id"]
                for row in conn.execute(
                    "SELECT id FROM T_Paises"
                ).fetchall()
            }

            available_subdivision_ids = {
                row["id"]
                for row in conn.execute(
                    "SELECT id FROM T_Subdivisiones_Administrativas"
                ).fetchall()
            }

            for row in rows:
                row_index = row.get("source_row_index", 0)
                result = self._ingest_localidad(
                    conn=conn,
                    row=row,
                    dry_run=dry_run,
                    existing_ids=existing_ids,
                    available_country_ids=available_country_ids,
                    available_subdivision_ids=available_subdivision_ids,
                )
                result.row_index = row_index
                results.append(result)

                if result.status == "inserted":
                    inserted += 1
                    if result.entity_id:
                        existing_ids.add(result.entity_id)
                elif result.status == "skipped_existing":
                    skipped_existing += 1
                    if result.entity_id:
                        existing_ids.add(result.entity_id)
                elif result.status == "failed":
                    failed += 1

            if dry_run:
                conn.rollback()
            else:
                conn.commit()

        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        return IngestionBatchResult(
            entity="T_Localidades",
            processed=len(rows),
            inserted=inserted,
            skipped_existing=skipped_existing,
            failed=failed,
            results=results,
        )

    def _ingest_localidad(
        self,
        conn: sqlite3.Connection,
        row: dict[str, Any],
        dry_run: bool,
        existing_ids: set[str],
        available_country_ids: set[str],
        available_subdivision_ids: set[str],
    ) -> IngestionRowResult:
        localidad_id = row.get("localidad_id")
        nombre = row.get("nombre")
        tipo_localidad = row.get("tipo_localidad")
        pais_id = row.get("pais_id")
        subdivision_id = row.get("subdivision_id")
        codigo_localidad = row.get("codigo_localidad")
        source_name = row.get("source_name")
        latitud = row.get("latitud")
        longitud = row.get("longitud")
        codigo_postal = row.get("codigo_postal")
        population = row.get("population")

        required = {
            "localidad_id": localidad_id,
            "nombre": nombre,
            "tipo_localidad": tipo_localidad,
            "pais_id": pais_id,
            "subdivision_id": subdivision_id,
            "codigo_localidad": codigo_localidad,
        }
        missing = [k for k, v in required.items() if not isinstance(v, str) or v.strip() == ""]
        if missing:
            return IngestionRowResult(
                row_index=0,
                status="failed",
                entity_id=localidad_id if isinstance(localidad_id, str) else None,
                errors=[
                    IngestionIssue(
                        code="missing_required_persistible_fields",
                        message=f"Faltan campos obligatorios persistibles en localidad: {', '.join(missing)}.",
                    )
                ],
            )

        if localidad_id in existing_ids:
            return IngestionRowResult(
                row_index=0,
                status="skipped_existing",
                entity_id=localidad_id,
            )

        if pais_id not in available_country_ids:
            return IngestionRowResult(
                row_index=0,
                status="failed",
                entity_id=localidad_id,
                errors=[
                    IngestionIssue(
                        code="country_not_found_in_db",
                        field="pais_id",
                        message=f"No existe pais_id='{pais_id}' en DB.",
                    )
                ],
            )

        if subdivision_id not in available_subdivision_ids:
            return IngestionRowResult(
                row_index=0,
                status="failed",
                entity_id=localidad_id,
                errors=[
                    IngestionIssue(
                        code="subdivision_not_found_in_db",
                        field="subdivision_id",
                        message=f"No existe subdivision_id='{subdivision_id}' en DB.",
                    )
                ],
            )

        existing_same_semantic = conn.execute(
            """
            SELECT id
            FROM T_Localidades
            WHERE pais_id = ?
              AND subdivision_id = ?
              AND nombre = ?
            """,
            (pais_id, subdivision_id, nombre),
        ).fetchone()

        if existing_same_semantic is not None:
            return IngestionRowResult(
                row_index=0,
                status="skipped_existing",
                entity_id=existing_same_semantic["id"],
            )

        if not dry_run:
            conn.execute(
                """
                INSERT INTO T_Localidades (
                    id,
                    nombre,
                    tipo_localidad,
                    pais_id,
                    subdivision_id,
                    codigo_localidad,
                    source_name,
                    latitud,
                    longitud,
                    codigo_postal,
                    population
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    localidad_id,
                    nombre,
                    tipo_localidad,
                    pais_id,
                    subdivision_id,
                    codigo_localidad,
                    source_name,
                    latitud,
                    longitud,
                    codigo_postal,
                    population,
                ),
            )

        return IngestionRowResult(
            row_index=0,
            status="inserted",
            entity_id=localidad_id,
        )

    def _ingest_subdivision(
        self,
        conn: sqlite3.Connection,
        row: dict[str, Any],
        dry_run: bool,
        available_ids: set[str],
    ) -> IngestionRowResult:
        subdivision_id = row.get("subdivision_id")
        nombre = row.get("nombre")
        tipo_subdivision = row.get("tipo_subdivision")
        nivel = row.get("nivel")
        pais_id = row.get("pais_id")
        parent_id = row.get("parent_id")
        codigo_subdivision = row.get("codigo_subdivision")
        source_name = row.get("source_name")

        required = {
            "subdivision_id": subdivision_id,
            "nombre": nombre,
            "tipo_subdivision": tipo_subdivision,
            "pais_id": pais_id,
        }
        missing = [k for k, v in required.items() if not isinstance(v, str) or v.strip() == ""]
        if missing or not isinstance(nivel, int):
            return IngestionRowResult(
                row_index=0,
                status="failed",
                entity_id=subdivision_id if isinstance(subdivision_id, str) else None,
                errors=[
                    IngestionIssue(
                        code="missing_required_persistible_fields",
                        message="Faltan campos obligatorios persistibles en subdivisión.",
                    )
                ],
            )

        # 1) Ya existe por ID
        if isinstance(subdivision_id, str) and subdivision_id in available_ids:
            return IngestionRowResult(
                row_index=0,
                status="skipped_existing",
                entity_id=subdivision_id,
            )

        # 2) Ya existe por identidad semántica en DB o por registros ya insertados
        existing_same_semantic = conn.execute(
            """
            SELECT id
            FROM T_Subdivisiones_Administrativas
            WHERE pais_id = ?
              AND nivel = ?
              AND nombre = ?
              AND (
                    (parent_id IS NULL AND ? IS NULL)
                    OR parent_id = ?
              )
            """,
            (pais_id, nivel, nombre, parent_id, parent_id),
        ).fetchone()

        if existing_same_semantic is not None:
            return IngestionRowResult(
                row_index=0,
                status="skipped_existing",
                entity_id=existing_same_semantic["id"],
            )

        # 3) Las de nivel 2 deben tener padre disponible ya sea en DB o en este batch
        if nivel == 2:
            if not isinstance(parent_id, str) or parent_id.strip() == "":
                return IngestionRowResult(
                    row_index=0,
                    status="failed",
                    entity_id=subdivision_id,
                    errors=[
                        IngestionIssue(
                            code="missing_parent_id",
                            field="parent_id",
                            message="Las subdivisiones de nivel 2 requieren parent_id.",
                        )
                    ],
                )

            if parent_id not in available_ids:
                return IngestionRowResult(
                    row_index=0,
                    status="failed",
                    entity_id=subdivision_id,
                    errors=[
                        IngestionIssue(
                            code="parent_not_found_in_db",
                            field="parent_id",
                            message=f"No existe parent_id='{parent_id}' disponible en esta carga ni en DB.",
                        )
                    ],
                )

        if not dry_run:
            conn.execute(
                """
                INSERT INTO T_Subdivisiones_Administrativas (
                    id,
                    nombre,
                    tipo_subdivision,
                    nivel,
                    pais_id,
                    parent_id,
                    codigo_subdivision,
                    source_name
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    subdivision_id,
                    nombre,
                    tipo_subdivision,
                    nivel,
                    pais_id,
                    parent_id,
                    codigo_subdivision,
                    source_name,
                ),
            )

        return IngestionRowResult(
            row_index=0,
            status="inserted",
            entity_id=subdivision_id,
        )
