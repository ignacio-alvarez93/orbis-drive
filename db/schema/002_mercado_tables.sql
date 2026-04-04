-- Orbis Drive
-- Schema generado desde Orbis_Drive.db
-- Bloque 002: tablas de mercado
-- Orden de ejecución: 002

PRAGMA foreign_keys = ON;

CREATE TABLE T_Concesionarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_normalizado TEXT NOT NULL UNIQUE,
    variantes TEXT
);

CREATE TABLE T_Anuncios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fuente TEXT NOT NULL,
    url TEXT NOT NULL,
    ide_coche TEXT NOT NULL,
    marca TEXT,
    modelo TEXT,
    version TEXT,
    version_normalizada TEXT,
    año INTEGER,
    kilometros INTEGER,
    precio_mostrado REAL,
    precio_contado REAL,
    precio_financiado REAL,
    color TEXT,
    tipo_transmision TEXT,
    tipo_vendedor TEXT,
    es_profesional INTEGER CHECK (es_profesional IN (0,1) OR es_profesional IS NULL),
    nombre_vendedor TEXT,
    concesionario_id INTEGER,
    ubicacion_raw TEXT,
    municipio_id INTEGER,
    provincia_id INTEGER,
    pais_id INTEGER,
    fecha_scrapeo DATETIME NOT NULL,
    first_seen DATETIME,
    last_seen DATETIME,
    estado_anuncio TEXT NOT NULL DEFAULT 'activo' CHECK (
        estado_anuncio IN ('activo', 'no_visto', 'inactivo_confirmado', 'reactivado')
    ),
    UNIQUE (fuente, ide_coche),
    CHECK (first_seen IS NULL OR last_seen IS NULL OR first_seen <= last_seen),
    CHECK (last_seen IS NULL OR fecha_scrapeo IS NULL OR last_seen <= fecha_scrapeo),
    FOREIGN KEY (concesionario_id) REFERENCES T_Concesionarios(id),
    FOREIGN KEY (municipio_id) REFERENCES T_Municipios(id),
    FOREIGN KEY (provincia_id) REFERENCES T_Provincias(id),
    FOREIGN KEY (pais_id) REFERENCES T_Paises(id)
);

CREATE TABLE T_Historico_Precios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anuncio_id INTEGER NOT NULL,
    fecha_scrapeo DATETIME NOT NULL,
    precio_mostrado REAL,
    precio_contado REAL,
    precio_financiado REAL,
    UNIQUE (anuncio_id, fecha_scrapeo),
    FOREIGN KEY (anuncio_id) REFERENCES T_Anuncios(id)
);
