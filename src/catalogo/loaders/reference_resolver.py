from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ResolvedReferences:
    manufacturer_id: int
    model_id: int
    generation_id: int | None


class ReferenceResolver:
    """
    Resuelve o crea referencias jerárquicas mínimas para la ingestión piloto.

    Reglas:
    - fabricante: se resuelve o crea si no existe
    - modelo: se resuelve o crea si no existe dentro del fabricante
    - generación: se resuelve si existe; si no hay certeza, se deja en NULL
    """

    def __init__(self, conn):
        self.conn = conn

    def resolve_or_create_manufacturer(self, row: dict[str, Any]) -> int:
        nombre = row["manufacturer_name"].strip()
        cur = self.conn.execute(
            "SELECT id FROM T_Fabricantes WHERE nombre = ?",
            (nombre,),
        )
        found = cur.fetchone()
        if found:
            return int(found[0])

        cur = self.conn.execute(
            "INSERT INTO T_Fabricantes (nombre) VALUES (?)",
            (nombre,),
        )
        return int(cur.lastrowid)

    def resolve_or_create_model(self, manufacturer_id: int, row: dict[str, Any]) -> int:
        nombre = row["model_name"].strip()
        cur = self.conn.execute(
            """
            SELECT id
            FROM T_Modelos
            WHERE manufacturer_id = ? AND nombre = ?
            """,
            (manufacturer_id, nombre),
        )
        found = cur.fetchone()
        if found:
            return int(found[0])

        cur = self.conn.execute(
            """
            INSERT INTO T_Modelos (manufacturer_id, nombre)
            VALUES (?, ?)
            """,
            (manufacturer_id, nombre),
        )
        return int(cur.lastrowid)

    def resolve_generation(self, manufacturer_id: int, model_id: int, row: dict[str, Any]) -> int | None:
        generation_name = row.get("generation_name")
        if not generation_name:
            return None

        cur = self.conn.execute(
            """
            SELECT id
            FROM T_Generaciones
            WHERE manufacturer_id = ? AND model_id = ? AND nombre = ?
            """,
            (manufacturer_id, model_id, generation_name.strip()),
        )
        found = cur.fetchone()
        if found:
            return int(found[0])

        return None

    def resolve_all(self, row: dict[str, Any]) -> ResolvedReferences:
        manufacturer_id = self.resolve_or_create_manufacturer(row)
        model_id = self.resolve_or_create_model(manufacturer_id, row)
        generation_id = self.resolve_generation(manufacturer_id, model_id, row)
        return ResolvedReferences(
            manufacturer_id=manufacturer_id,
            model_id=model_id,
            generation_id=generation_id,
        )
