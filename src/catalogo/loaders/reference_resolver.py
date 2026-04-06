from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ResolvedReferences:
    manufacturer_id: str
    model_id: str
    generation_id: str


class ReferenceResolver:
    """
    Para la ingestión piloto actual NO resuelve ni crea jerarquía.
    Consume directamente el dataset ya resuelto por ID_RESOLUTION.
    """

    def __init__(self, conn):
        self.conn = conn

    def resolve_all(self, row: dict[str, Any]) -> ResolvedReferences:
        manufacturer_id = row.get("manufacturer_id")
        model_id = row.get("model_id")
        generation_id = row.get("generation_id")

        if not manufacturer_id:
            raise ValueError("Falta 'manufacturer_id' en el dataset resuelto.")
        if not model_id:
            raise ValueError("Falta 'model_id' en el dataset resuelto.")
        if not generation_id:
            raise ValueError("Falta 'generation_id' en el dataset resuelto.")

        return ResolvedReferences(
            manufacturer_id=str(manufacturer_id),
            model_id=str(model_id),
            generation_id=str(generation_id),
        )