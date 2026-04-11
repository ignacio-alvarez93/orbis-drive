# SEMANTIC_ENRICHMENT_LAYER — Paquete de implementación

Este paquete contiene una implementación base lista para integrar en Orbis Drive de la nueva capa:

```text
SCRAPER → DICT LIMPIO → IIG → DVL → VALIDACIÓN DE LOTE → ENRICHMENT → ID_RESOLUTION → INGESTIÓN
```

## Contenido

- `src/catalogo/enrichment/` → código fuente
- `tests/unit/catalogo/enrichment/` → tests unitarios
- `PATCH_PIPELINE_EXAMPLE.md` → ejemplo de integración en pipeline
- `PASOS_IMPLEMENTACION.md` → secuencia recomendada de implantación

## Filosofía

- No modifica el dato original
- No infiere datos no deterministas
- No altera `semantic_key`
- Solo explicita campos ya implícitos
