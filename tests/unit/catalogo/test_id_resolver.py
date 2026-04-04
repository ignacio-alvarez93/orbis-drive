
from __future__ import annotations

import sqlite3

import pytest

from src.catalogo.pipeline.id_resolution.id_resolver import (
    IDResolutionError,
    TVersionesIDResolver,
    canonicalize_version_name,
    slugify,
)


def make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    conn.executescript(
        """
        CREATE TABLE T_Fabricantes (
            manufacturer_id TEXT PRIMARY KEY,
            manufacturer_name TEXT,
            manufacturer_name_upper TEXT,
            manufacturer_href_relative TEXT,
            manufacturer_href_absolute TEXT
        );

        CREATE TABLE T_Modelos (
            manufacturer_id TEXT NOT NULL,
            manufacturer_name TEXT,
            manufacturer_name_upper TEXT,
            model_id TEXT PRIMARY KEY,
            model_name TEXT,
            model_name_upper TEXT,
            model_href_relative TEXT,
            model_href_absolute TEXT
        );

        CREATE TABLE T_Generaciones (
            manufacturer_id TEXT NOT NULL,
            manufacturer_name TEXT,
            manufacturer_name_upper TEXT,
            model_id TEXT NOT NULL,
            model_name TEXT,
            model_name_upper TEXT,
            generation_id TEXT PRIMARY KEY,
            generation_name TEXT,
            generation_name_canonical TEXT,
            generation_name_upper TEXT,
            year_start INTEGER,
            year_end TEXT,
            year_end_raw TEXT,
            generation_href_relative TEXT,
            generation_href_absolute TEXT
        );
        """
    )

    conn.execute(
        """
        INSERT INTO T_Fabricantes (
            manufacturer_id, manufacturer_name, manufacturer_name_upper
        ) VALUES (?, ?, ?)
        """,
        ("seat", "SEAT", "SEAT"),
    )

    conn.execute(
        """
        INSERT INTO T_Modelos (
            manufacturer_id, manufacturer_name, manufacturer_name_upper,
            model_id, model_name, model_name_upper
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("seat", "SEAT", "SEAT", "seat_ibiza", "Ibiza", "IBIZA"),
    )

    conn.execute(
        """
        INSERT INTO T_Generaciones (
            manufacturer_id, manufacturer_name, manufacturer_name_upper,
            model_id, model_name, model_name_upper,
            generation_id, generation_name, generation_name_canonical, generation_name_upper
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "seat", "SEAT", "SEAT",
            "seat_ibiza", "Ibiza", "IBIZA",
            "seat_ibiza_mk5", "Mk5", "mk5", "MK5"
        ),
    )
    return conn


def test_slugify():
    assert slugify("1.5 TSI 150 FR DSG") == "1_5_tsi_150_fr_dsg"


def test_canonicalize_version_name():
    assert canonicalize_version_name("1.0 TSI 95 FR") == "1_0_tsi_95_fr"


def test_transform_row_ok():
    conn = make_conn()
    resolver = TVersionesIDResolver(conn)

    row = {
        "manufacturer_name": "SEAT",
        "model_name": "Ibiza",
        "generation_name": "Mk5",
        "version_name": "1.0 TSI 95 FR",
        "gearbox": "manual",
        "traction": "fwd",
    }

    out = resolver.transform_row(row)

    assert out["manufacturer_id"] == "seat"
    assert out["model_id"] == "seat_ibiza"
    assert out["generation_id"] == "seat_ibiza_mk5"
    assert out["version_name_canonical"] == "1_0_tsi_95_fr"
    assert out["version_id"] == "seat_ibiza_mk5_1_0_tsi_95_fr"
    assert out["gearbox_type"] == "manual"
    assert out["drive_type"] == "fwd"


def test_transform_row_fails_if_generation_not_found():
    conn = make_conn()
    resolver = TVersionesIDResolver(conn)

    row = {
        "manufacturer_name": "SEAT",
        "model_name": "Ibiza",
        "generation_name": "Mk4",
        "version_name": "1.0 TSI 95 FR",
    }

    with pytest.raises(IDResolutionError):
        resolver.transform_row(row)
