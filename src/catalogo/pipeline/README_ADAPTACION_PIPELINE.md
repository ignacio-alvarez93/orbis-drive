# Adaptación del pipeline para SEMANTIC_ENRICHMENT_LAYER

## Qué cambia

Se inserta `ENRICHMENT` entre:

`VALIDACIÓN DE LOTE -> ENRICHMENT -> ID_RESOLUTION -> INGESTIÓN`

## Cambios aplicados al fichero

1. Nuevo import:
   `from src.catalogo.enrichment.core.enrichment_engine import EnrichmentEngine`

2. Nueva dependencia en `__init__`:
   `self.enrichment_engine = EnrichmentEngine()`

3. Nuevo método:
   `_build_row_for_resolution(...)`

4. En `run(...)`:
   - se ejecuta enrichment después de `_prevalidate_row`
   - `ReferenceResolver` resuelve sobre `row_for_resolution`
   - `loader.insert_one(...)` recibe `row_for_resolution`
   - se adjunta resumen de enrichment a `record_ref`

## Qué NO cambia

- no se modifica `row` original
- no se altera `semantic_key`
- no se mueve lógica a DVL
- no se toca ID_RESOLUTION más allá del payload de entrada

## Orden recomendado de despliegue

1. Añadir `src/catalogo/enrichment/`
2. Añadir tests de enrichment
3. Sustituir `src/catalogo/pipeline/ingestion_pipeline.py` por esta versión
4. Ejecutar:
   `pytest -q`
5. Ejecutar un lote piloto real y revisar `record_ref["enrichment"]`
