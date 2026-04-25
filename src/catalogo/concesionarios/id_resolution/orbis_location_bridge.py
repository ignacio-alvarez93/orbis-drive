from __future__ import annotations

import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import Optional

from ..models.concesionario_normalized import ConcesionarioNormalized
from .location_aliases import LOCALITY_ALIASES, PROVINCE_ALIASES
from .location_resolver_adapter import LocationResolutionResult


class OrbisLocationBridge:
    """
    Bridge real entre T_Concesionarios y la base territorial ya ingerida en SQLite.

    V1 reforzada para España:
    - país ES
    - provincia por nombre
    - localidad por nombre
    - aliases controlados externos
    - apoyo por código postal
    """

    SPAIN_MARKERS = {
        "es",
        "espana",
        "españa",
        "spain",
    }

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    def resolve_concesionario_location(
        self,
        normalized: ConcesionarioNormalized,
    ) -> LocationResolutionResult:
        if not self.db_path.exists():
            return LocationResolutionResult(
                pais_id=None,
                subdivision_id=None,
                localidad_id=None,
                is_resolved=False,
                reason=f"db_path no existe: {self.db_path}",
            )

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            pais_id = self._resolve_country_id(conn)
            if not pais_id:
                return LocationResolutionResult(
                    pais_id=None,
                    subdivision_id=None,
                    localidad_id=None,
                    is_resolved=False,
                    reason="no se pudo resolver pais_id",
                )

            province_name = self._extract_province_candidate(normalized)
            subdivision_id = self._resolve_subdivision_id(conn, pais_id, province_name)

            locality_name = self._extract_locality_candidate(normalized)
            localidad_id = self._resolve_localidad_id(
                conn=conn,
                pais_id=pais_id,
                subdivision_id=subdivision_id,
                locality_name=locality_name,
                postal_code=normalized.codigo_postal_normalizado,
            )

            if localidad_id:
                return LocationResolutionResult(
                    pais_id=pais_id,
                    subdivision_id=subdivision_id,
                    localidad_id=localidad_id,
                    is_resolved=True,
                    reason=None,
                )

            reason_parts = []
            if province_name:
                reason_parts.append(f"provincia='{province_name}'")
            if locality_name:
                reason_parts.append(f"localidad='{locality_name}'")
            if normalized.codigo_postal_normalizado:
                reason_parts.append(f"cp='{normalized.codigo_postal_normalizado}'")

            detail = ", ".join(reason_parts) if reason_parts else "sin candidatos suficientes"

            return LocationResolutionResult(
                pais_id=pais_id,
                subdivision_id=subdivision_id,
                localidad_id=None,
                is_resolved=False,
                reason=f"no se pudo resolver localidad_id ({detail})",
            )

    def _resolve_country_id(self, conn: sqlite3.Connection) -> Optional[str]:
        row = conn.execute(
            """
            SELECT id
            FROM T_Paises
            WHERE codigo_iso = 'ES'
            LIMIT 1
            """
        ).fetchone()

        return row["id"] if row else None

    def _extract_province_candidate(
        self,
        normalized: ConcesionarioNormalized,
    ) -> Optional[str]:
        texts = [
            normalized.raw.location_raw,
            normalized.raw.address_raw,
            normalized.direccion_texto_normalizada,
        ]

        normalized_texts = []
        for text in texts:
            if text:
                normalized_texts.append(self._normalize_cmp(text))

        for raw_text in normalized_texts:
            for alias, canonical in PROVINCE_ALIASES.items():
                alias_norm = self._normalize_cmp(alias)
                if alias_norm in raw_text:
                    return canonical

        return None

    def _extract_locality_candidate(
        self,
        normalized: ConcesionarioNormalized,
    ) -> Optional[str]:
        location_raw = (normalized.raw.location_raw or "").strip()
        if not location_raw:
            return None

        parts = [p.strip() for p in location_raw.split(",") if p.strip()]
        candidate = parts[0] if parts else location_raw

        candidate_norm = self._normalize_cmp(candidate)
        if candidate_norm in self.SPAIN_MARKERS:
            return None

        # Si viene como "Localidad Provincia", recortar provincia final
        for alias, canonical in PROVINCE_ALIASES.items():
            alias_norm = self._normalize_cmp(alias)
            canonical_norm = self._normalize_cmp(canonical)

            for province_token in {alias_norm, canonical_norm}:
                suffix = f" {province_token}"
                if candidate_norm.endswith(suffix):
                    stripped = candidate_norm[: -len(suffix)].strip()
                    if stripped:
                        return self._apply_locality_alias(stripped)

        return self._apply_locality_alias(candidate)

    def _apply_locality_alias(self, locality_name: str) -> str:
        normalized = self._normalize_cmp(locality_name)
        return LOCALITY_ALIASES.get(normalized, locality_name)

    def _resolve_subdivision_id(
        self,
        conn: sqlite3.Connection,
        pais_id: str,
        province_name: Optional[str],
    ) -> Optional[str]:
        if not province_name:
            return None

        rows = conn.execute(
            """
            SELECT id, nombre
            FROM T_Subdivisiones_Administrativas
            WHERE pais_id = ?
              AND nivel = 2
            """,
            (pais_id,),
        ).fetchall()

        target = self._normalize_cmp(province_name)

        for row in rows:
            if self._normalize_cmp(row["nombre"]) == target:
                return row["id"]

        return None

    def _resolve_localidad_id(
        self,
        conn: sqlite3.Connection,
        pais_id: str,
        subdivision_id: Optional[str],
        locality_name: Optional[str],
        postal_code: Optional[str],
    ) -> Optional[str]:
        if not locality_name:
            return None

        target = self._normalize_cmp(locality_name)

        if subdivision_id:
            rows = conn.execute(
                """
                SELECT id, nombre, codigo_postal
                FROM T_Localidades
                WHERE pais_id = ?
                  AND subdivision_id = ?
                """,
                (pais_id, subdivision_id),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, nombre, codigo_postal
                FROM T_Localidades
                WHERE pais_id = ?
                """,
                (pais_id,),
            ).fetchall()

        exact_matches = []
        for row in rows:
            if self._normalize_cmp(row["nombre"]) == target:
                exact_matches.append(row)

        if len(exact_matches) == 1:
            return exact_matches[0]["id"]

        if len(exact_matches) > 1 and postal_code:
            for row in exact_matches:
                row_cp = (row["codigo_postal"] or "").strip()
                if row_cp == postal_code:
                    return row["id"]

        if postal_code and not subdivision_id:
            rows_cp = conn.execute(
                """
                SELECT id, nombre, codigo_postal
                FROM T_Localidades
                WHERE pais_id = ?
                  AND codigo_postal = ?
                """,
                (pais_id, postal_code),
            ).fetchall()

            cp_name_matches = []
            for row in rows_cp:
                if self._normalize_cmp(row["nombre"]) == target:
                    cp_name_matches.append(row)

            if len(cp_name_matches) == 1:
                return cp_name_matches[0]["id"]

        return None

    @staticmethod
    def _normalize_cmp(value: str) -> str:
        value = value.strip().lower()
        value = unicodedata.normalize("NFKD", value)
        value = "".join(ch for ch in value if not unicodedata.combining(ch))

        value = value.replace("’", "'").replace("`", "'")
        value = value.replace("'", " ")
        value = value.replace("-", " ")

        value = re.sub(r"[^\w\s/]", " ", value)
        value = re.sub(r"\s+", " ", value)

        return value.strip()