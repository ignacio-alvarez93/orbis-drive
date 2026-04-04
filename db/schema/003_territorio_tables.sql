-- Orbis Drive
-- Schema generado desde Orbis_Drive.db
-- Bloque 003: tablas territoriales presentes en la SQLite actual
-- AVISO: este bloque refleja el modelo territorial legado detectado en la DB

PRAGMA foreign_keys = ON;

CREATE TABLE T_Paises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE T_Provincias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    pais_id INTEGER NOT NULL,
    UNIQUE (nombre, pais_id),
    FOREIGN KEY (pais_id) REFERENCES T_Paises(id)
);

CREATE TABLE T_Municipios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    provincia_id INTEGER NOT NULL,
    UNIQUE (nombre, provincia_id),
    FOREIGN KEY (provincia_id) REFERENCES T_Provincias(id)
);
