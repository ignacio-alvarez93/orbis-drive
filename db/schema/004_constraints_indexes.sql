-- Orbis Drive
-- Índices explícitos extraídos desde Orbis_Drive.db

PRAGMA foreign_keys = ON;

-- T_Modelos
CREATE INDEX idx_modelos_manufacturer_id
    ON T_Modelos(manufacturer_id);

-- T_Generaciones
CREATE INDEX idx_generaciones_manufacturer_id
    ON T_Generaciones(manufacturer_id);
CREATE INDEX idx_generaciones_model_id
    ON T_Generaciones(model_id);

-- T_Versiones
CREATE INDEX idx_versiones_drive_type
ON T_Versiones(drive_type);
CREATE INDEX idx_versiones_fuel_type
ON T_Versiones(fuel_type);
CREATE INDEX idx_versiones_generation_id
ON T_Versiones(generation_id);
CREATE INDEX idx_versiones_manufacturer_id
ON T_Versiones(manufacturer_id);
CREATE INDEX idx_versiones_model_id
ON T_Versiones(model_id);
CREATE INDEX idx_versiones_power_cv
ON T_Versiones(power_cv);
CREATE INDEX idx_versiones_version_name_canonical
ON T_Versiones(version_name_canonical);

-- T_Anuncios
CREATE INDEX idx_anuncios_es_profesional ON T_Anuncios(es_profesional);
CREATE INDEX idx_anuncios_estado ON T_Anuncios(estado_anuncio);
CREATE INDEX idx_anuncios_fecha_scrapeo ON T_Anuncios(fecha_scrapeo);
CREATE INDEX idx_anuncios_first_seen ON T_Anuncios(first_seen);
CREATE INDEX idx_anuncios_fuente ON T_Anuncios(fuente);
CREATE INDEX idx_anuncios_ide_coche ON T_Anuncios(ide_coche);
CREATE INDEX idx_anuncios_last_seen ON T_Anuncios(last_seen);
CREATE INDEX idx_anuncios_municipio ON T_Anuncios(municipio_id);
CREATE INDEX idx_anuncios_precio_mostrado ON T_Anuncios(precio_mostrado);
CREATE INDEX idx_anuncios_provincia ON T_Anuncios(provincia_id);
CREATE INDEX idx_anuncios_vendedor ON T_Anuncios(nombre_vendedor);

-- T_Historico_Precios
CREATE INDEX idx_historico_anuncio ON T_Historico_Precios(anuncio_id);
CREATE INDEX idx_historico_fecha ON T_Historico_Precios(fecha_scrapeo);

-- T_Provincias
CREATE INDEX idx_provincias_pais ON T_Provincias(pais_id);

-- T_Municipios
CREATE INDEX idx_municipios_provincia ON T_Municipios(provincia_id);
