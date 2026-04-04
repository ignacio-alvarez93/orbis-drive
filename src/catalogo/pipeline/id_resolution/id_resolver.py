from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any


class IDResolutionError(Exception):
    """Error controlado de resolución de identidad."""
    pass


def _canon(text: str | None) -> str:
    if not text:
        return ""
    text = text.strip().lower()
    text = re.sub(r"[()]", " ", text)
    text = re.sub(r"[^a-z0-9áéíóúüñ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _slug(text: str | None) -> str:
    value = _canon(text)
    return value.replace(" ", "_")


IBIZA_GENERATION_ALIASES = {
    "mk5": ["ibiza 2017 actualidad", "ibiza 2017-actualidad"],
    "mk4": ["ibiza 2008 2017", "ibiza 2008-2017"],
    "mk3": ["ibiza 2002 2009", "ibiza 2002-2009"],
    "mk2": ["ibiza 1993 2002", "ibiza 1993-2002"],
    "mk1": ["ibiza 1984 1993", "ibiza 1984-1993"],
}


class IDResolver:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self) -> None:
        self.conn.close()

    def resolve_manufacturer_id(self, manufacturer_name: str) -> str:
        target = _canon(manufacturer_name)
        rows = self.conn.execute(
            """
            SELECT manufacturer_id, manufacturer_name, manufacturer_name_upper
            FROM T_Fabricantes
            """
        ).fetchall()

        for row in rows:
            candidates = {
                _canon(row["manufacturer_id"]),
                _canon(row["manufacturer_name"]),
                _canon(row["manufacturer_name_upper"]),
            }
            if target in candidates:
                return row["manufacturer_id"]

        raise IDResolutionError(
            f"No existe fabricante resoluble en DB para manufacturer_name={manufacturer_name!r}"
        )

    def resolve_model_id(self, manufacturer_id: str, model_name: str) -> str:
        target = _canon(model_name)
        rows = self.conn.execute(
            """
            SELECT model_id, model_name, model_name_upper
            FROM T_Modelos
            WHERE manufacturer_id = ?
            """,
            (manufacturer_id,),
        ).fetchall()

        for row in rows:
            candidates = {
                _canon(row["model_id"]),
                _canon(row["model_name"]),
                _canon(row["model_name_upper"]),
            }
            if target in candidates:
                return row["model_id"]

        raise IDResolutionError(
            f"No existe modelo resoluble en DB para manufacturer_id={manufacturer_id!r}, model_name={model_name!r}"
        )

    def resolve_generation_id(self, model_id: str, generation_name: str) -> str:
        rows = self.conn.execute(
            """
            SELECT generation_id, generation_name, generation_name_canonical
            FROM T_Generaciones
            WHERE model_id = ?
            """,
            (model_id,),
        ).fetchall()

        target = _canon(generation_name)

        for row in rows:
            candidates = {
                _canon(row["generation_id"]),
                _canon(row["generation_name"]),
                _canon(row["generation_name_canonical"]),
            }
            if target in candidates:
                return row["generation_id"]

        aliases = IBIZA_GENERATION_ALIASES.get(target, [])
        if aliases:
            alias_set = {_canon(a) for a in aliases}
            for row in rows:
                if _canon(row["generation_name"]) in alias_set or _canon(row["generation_name_canonical"]) in alias_set:
                    return row["generation_id"]

        raise IDResolutionError(
            f"No existe generación resoluble en DB para model_id={model_id!r}, generation_name={generation_name!r}"
        )

    def resolve_row(self, row: dict[str, Any], row_index: int) -> dict[str, Any]:
        manufacturer_name = row.get("manufacturer_name")
        model_name = row.get("model_name")
        generation_name = row.get("generation_name")
        version_name = row.get("version_name")

        if not manufacturer_name or not model_name or not generation_name or not version_name:
            raise IDResolutionError(
                f"Fila {row_index}: faltan campos mínimos para resolución de identidad"
            )

        manufacturer_id = self.resolve_manufacturer_id(manufacturer_name)
        model_id = self.resolve_model_id(manufacturer_id, model_name)
        generation_id = self.resolve_generation_id(model_id, generation_name)
        version_name_canonical = _slug(version_name)
        version_id = f"{generation_id}__{version_name_canonical}"

        resolved = dict(row)
        resolved["manufacturer_id"] = manufacturer_id
        resolved["model_id"] = model_id
        resolved["generation_id"] = generation_id
        resolved["version_name_canonical"] = version_name_canonical
        resolved["version_id"] = version_id

        gearbox = row.get("gearbox")
        traction = row.get("traction")
        if gearbox and "gearbox_type" not in resolved:
            resolved["gearbox_type"] = gearbox
        if traction and "drive_type" not in resolved:
            resolved["drive_type"] = traction

        return resolved


def resolve_t_versiones_ids(db_path: str, input_path: str, output_path: str) -> list[dict[str, Any]]:
    input_rows = json.loads(Path(input_path).read_text(encoding="utf-8"))
    if not isinstance(input_rows, list):
        raise IDResolutionError("El input debe ser una lista JSON de registros.")

    resolver = IDResolver(db_path)
    try:
        output_rows = []
        for idx, row in enumerate(input_rows, start=1):
            try:
                output_rows.append(resolver.resolve_row(row, idx))
            except IDResolutionError as exc:
                raise IDResolutionError(str(exc)) from exc

        Path(output_path).write_text(
            json.dumps(output_rows, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output_rows
    finally:
        resolver.close()


def resolve_dataset_file(db_path: str, input_path: str, output_path: str) -> list[dict[str, Any]]:
    """Alias de compatibilidad para el runner actual."""
    return resolve_t_versiones_ids(db_path=db_path, input_path=input_path, output_path=output_path)
