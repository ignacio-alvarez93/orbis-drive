PRAGMA foreign_keys = ON;

-- ============================================================
-- T_Paises
-- Pilar territorial base (nivel país)
-- ============================================================

CREATE TABLE IF NOT EXISTS T_Paises (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    codigo_iso TEXT NOT NULL,
    codigo_iso3 TEXT NOT NULL,
    region_global TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_t_paises_iso2
ON T_Paises (codigo_iso);

CREATE UNIQUE INDEX IF NOT EXISTS idx_t_paises_iso3
ON T_Paises (codigo_iso3);

CREATE INDEX IF NOT EXISTS idx_t_paises_nombre
ON T_Paises (nombre);

-- ============================================================
-- T_Subdivisiones_Administrativas
-- Jerarquía territorial intermedia (nivel país → región → ...)
-- ============================================================

CREATE TABLE IF NOT EXISTS T_Subdivisiones_Administrativas (

    -- Identidad técnica (ID_RESOLUTION)
    id TEXT PRIMARY KEY,

    -- Nombre canónico
    nombre TEXT NOT NULL,

    -- Tipo de subdivisión (ej: comunidad_autonoma, provincia, region)
    tipo_subdivision TEXT NOT NULL,

    -- Nivel jerárquico (1, 2, 3...)
    nivel INTEGER NOT NULL,

    -- Relación con país
    pais_id TEXT NOT NULL,

    -- Relación jerárquica interna
    parent_id TEXT,

    -- Código administrativo (opcional pero recomendable)
    codigo_subdivision TEXT,

    -- Nombre original fuente (trazabilidad)
    source_name TEXT,

    -- Metadatos sistema
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (pais_id) REFERENCES T_Paises(id),
    FOREIGN KEY (parent_id) REFERENCES T_Subdivisiones_Administrativas(id)
);
-- Búsqueda por país
CREATE INDEX IF NOT EXISTS idx_t_subdivisiones_pais
ON T_Subdivisiones_Administrativas (pais_id);

-- Navegación jerárquica
CREATE INDEX IF NOT EXISTS idx_t_subdivisiones_parent
ON T_Subdivisiones_Administrativas (parent_id);

-- Filtrado por nivel
CREATE INDEX IF NOT EXISTS idx_t_subdivisiones_nivel
ON T_Subdivisiones_Administrativas (nivel);

-- Búsqueda por nombre
CREATE INDEX IF NOT EXISTS idx_t_subdivisiones_nombre
ON T_Subdivisiones_Administrativas (nombre);
CREATE UNIQUE INDEX IF NOT EXISTS idx_t_subdivisiones_unique
ON T_Subdivisiones_Administrativas (
    pais_id,
    nivel,
    nombre,
    parent_id
);
-- ============================================================
-- T_Localidades
-- Entidad territorial local reusable y multipaís
-- ============================================================

CREATE TABLE IF NOT EXISTS T_Localidades (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    tipo_localidad TEXT NOT NULL,
    pais_id TEXT NOT NULL,
    subdivision_id TEXT NOT NULL,
    codigo_localidad TEXT,
    source_name TEXT,
    latitud REAL,
    longitud REAL,
    codigo_postal TEXT,
    population INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pais_id) REFERENCES T_Paises(id),
    FOREIGN KEY (subdivision_id) REFERENCES T_Subdivisiones_Administrativas(id)
);

CREATE INDEX IF NOT EXISTS idx_t_localidades_pais
ON T_Localidades (pais_id);

CREATE INDEX IF NOT EXISTS idx_t_localidades_subdivision
ON T_Localidades (subdivision_id);

CREATE INDEX IF NOT EXISTS idx_t_localidades_nombre
ON T_Localidades (nombre);

CREATE UNIQUE INDEX IF NOT EXISTS idx_t_localidades_unique
ON T_Localidades (pais_id, subdivision_id, nombre);
-- ============================================================
-- T_Direcciones
-- Capa de precisión territorial opcional, preparada para Orbis-Geo
-- ============================================================

CREATE TABLE IF NOT EXISTS T_Direcciones (
    id TEXT PRIMARY KEY,

    -- Relación territorial base
    localidad_id TEXT NOT NULL,

    -- Componentes principales de dirección
    via_nombre TEXT,
    numero TEXT,
    bloque TEXT,
    portal TEXT,
    escalera TEXT,
    planta TEXT,
    puerta TEXT,

    -- Complementos
    codigo_postal TEXT,
    direccion_texto TEXT,

    -- Preparado para Orbis-Geo
    latitud REAL,
    longitud REAL,

    -- Trazabilidad
    source_name TEXT,

    -- Metadatos sistema
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (localidad_id) REFERENCES T_Localidades(id)
);

CREATE INDEX IF NOT EXISTS idx_t_direcciones_localidad
ON T_Direcciones (localidad_id);

CREATE INDEX IF NOT EXISTS idx_t_direcciones_codigo_postal
ON T_Direcciones (codigo_postal);

CREATE INDEX IF NOT EXISTS idx_t_direcciones_via_nombre
ON T_Direcciones (via_nombre);

CREATE INDEX IF NOT EXISTS idx_t_direcciones_lat_lon
ON T_Direcciones (latitud, longitud);

CREATE UNIQUE INDEX IF NOT EXISTS idx_t_direcciones_unique
ON T_Direcciones (
    localidad_id,
    via_nombre,
    numero,
    bloque,
    portal,
    escalera,
    planta,
    puerta,
    codigo_postal
);