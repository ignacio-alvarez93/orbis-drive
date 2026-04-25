from __future__ import annotations

import sqlite3
from datetime import datetime


class TConcesionariosLoader:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def insert_concesionario(self, conn: sqlite3.Connection, r) -> None:
        now = datetime.utcnow().isoformat()

        conn.execute(
            """
            INSERT INTO T_Concesionarios (
                concesionario_id,
                semantic_key_concesionario,
                nombre,
                nombre_canonical,
                tipo_concesionario,
                pais_id,
                subdivision_id,
                localidad_id,
                direccion_texto,
                codigo_postal,
                ubicacion_raw,
                telefono,
                email,
                website_url,
                website_domain,
                instagram_profile_url,
                facebook_page_url,
                tiktok_profile_url,
                youtube_channel_url,
                google_business_profile_url,
                source_name,
                source_row_url,
                record_external_id,
                scrape_date,
                created_at,
                updated_at,
                is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r.concesionario_id,
                r.semantic_key_concesionario,
                r.validated.normalized.raw.dealer_name_raw,
                r.validated.normalized.nombre_canonical,
                r.validated.normalized.tipo_concesionario_normalizado,
                r.pais_id,
                r.subdivision_id,
                r.localidad_id,
                r.validated.normalized.direccion_texto_normalizada,
                r.validated.normalized.codigo_postal_normalizado,
                r.validated.normalized.raw.location_raw,
                r.validated.normalized.raw.phone_raw,
                r.validated.normalized.raw.email_raw,
                r.validated.normalized.raw.website_raw,
                r.validated.normalized.website_domain,
                r.validated.normalized.raw.instagram_raw,
                r.validated.normalized.raw.facebook_raw,
                r.validated.normalized.raw.tiktok_raw,
                r.validated.normalized.raw.youtube_raw,
                r.validated.normalized.raw.google_business_profile_raw,
                r.validated.normalized.raw.source_name,
                r.validated.normalized.raw.source_row_url,
                r.validated.normalized.raw.record_external_id,
                r.validated.normalized.raw.scrape_date,
                now,
                now,
                1,
            ),
        )

    def batch_insert(self, records: list) -> dict:
        inserted = 0
        duplicates = 0
        failed = 0
        errors = []

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")

            for r in records:
                try:
                    self.insert_concesionario(conn, r)
                    inserted += 1

                except sqlite3.IntegrityError as exc:
                    duplicates += 1
                    errors.append({
                        "type": "IntegrityError",
                        "concesionario_id": r.concesionario_id,
                        "semantic_key": r.semantic_key_concesionario,
                        "error": str(exc),
                    })

                except Exception as exc:
                    failed += 1
                    errors.append({
                        "type": type(exc).__name__,
                        "concesionario_id": getattr(r, "concesionario_id", None),
                        "semantic_key": getattr(r, "semantic_key_concesionario", None),
                        "error": str(exc),
                    })

            conn.commit()

        return {
            "inserted": inserted,
            "duplicates": duplicates,
            "failed": failed,
            "errors": errors[:10],
        }