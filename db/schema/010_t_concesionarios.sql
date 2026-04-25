CREATE TABLE IF NOT EXISTS T_Concesionarios (

    concesionario_id TEXT PRIMARY KEY,
    semantic_key_concesionario TEXT NOT NULL UNIQUE,

    -- identidad
    nombre TEXT NOT NULL,
    nombre_canonical TEXT NOT NULL,

    -- clasificación
    tipo_concesionario TEXT,

    -- ubicación
    pais_id TEXT NOT NULL,
    subdivision_id TEXT,
    localidad_id TEXT,
    direccion_texto TEXT,
    codigo_postal TEXT,
    ubicacion_raw TEXT NOT NULL,

    -- contacto (opcional)
    telefono TEXT,
    email TEXT,
    website_url TEXT,
    website_domain TEXT,

    -- presencia digital (solo referencias)
    instagram_profile_url TEXT,
    facebook_page_url TEXT,
    tiktok_profile_url TEXT,
    youtube_channel_url TEXT,
    google_business_profile_url TEXT,

    -- metadata
    source_name TEXT NOT NULL,
    source_row_url TEXT NOT NULL,
    record_external_id TEXT,
    scrape_date TEXT NOT NULL,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,

    FOREIGN KEY (pais_id) REFERENCES T_Paises(id),
    FOREIGN KEY (subdivision_id) REFERENCES T_Subdivisiones_Administrativas(id),
    FOREIGN KEY (localidad_id) REFERENCES T_Localidades(id)
);