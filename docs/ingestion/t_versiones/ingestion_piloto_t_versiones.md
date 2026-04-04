# Ingestión piloto de T_Versiones

## Objetivo

Conectar el pipeline validado de catálogo con la base de datos real mediante una carga pequeña, controlada, reproducible y trazable.

## Flujo

```text
DATASET VALIDADO
    ↓
Precheck de ingestión
    ↓
Resolución jerárquica
    ↓
Control anti-duplicado
    ↓
Inserción transaccional en T_Versiones
    ↓
Resumen de ingestión
```

## Reglas

- El input debe venir de salida validada, nunca desde HTML.
- El lote piloto debe tener entre 3 y 5 registros.
- Cada registro debe venir con `iig_status=passed`, `dvl_status=passed` y `batch_status=passed`.
- La ingestión no corrige ni reconstruye datos.
- Si la generación no es resoluble con seguridad, se deja `NULL`.
- En modo estricto, cualquier fallo provoca `rollback` del lote.

## Archivos principales

- `src/catalogo/loaders/ingestion_report.py`
- `src/catalogo/loaders/reference_resolver.py`
- `src/catalogo/loaders/t_versiones_loader.py`
- `src/catalogo/pipeline/ingestion_pipeline.py`
- `scripts/ingestion/run_t_versiones_pilot_ingestion.py`

## Ejecución

```bash
PYTHONPATH=. python scripts/ingestion/run_t_versiones_pilot_ingestion.py \
  --db-path db/orbis_drive.sqlite \
  --dataset data/samples/input/lote_t_versiones_pilot_validado.json
```

## Salida esperada

- total procesado
- insertados
- omitidos por duplicado
- fallidos
- tablas afectadas
- detalle por fila


La base de datos operativa local de Orbis Drive debe residir en `db/local/orbis_drive.sqlite` y no debe versionarse. El repositorio solo contiene esquema, migraciones, seeds y documentación técnica.
