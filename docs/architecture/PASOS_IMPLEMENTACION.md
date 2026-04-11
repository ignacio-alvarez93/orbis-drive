# Pasos para implementar en tu repositorio Orbis Drive

## 1. Copiar carpetas al repositorio

Copia estas rutas dentro de tu repo:

- `src/catalogo/enrichment/`
- `tests/unit/catalogo/enrichment/`

## 2. Verificar imports

Confirma que tu proyecto resuelve imports tipo:

```python
from src.catalogo.enrichment.core.enrichment_engine import EnrichmentEngine
```

Si ejecutas `pytest` desde la raíz del repo, con tu estructura actual debería funcionar.

## 3. Integrar la capa en el pipeline

La integración debe hacerse **después de VALIDACIÓN DE LOTE** y **antes de ID_RESOLUTION**.

Orden correcto:

```text
VALIDACIÓN DE LOTE → ENRICHMENT → ID_RESOLUTION
```

## 4. Crear instancia del engine

En el punto de orquestación principal:

```python
from src.catalogo.enrichment.core.enrichment_engine import EnrichmentEngine

enrichment_engine = EnrichmentEngine()
```

## 5. Ejecutar enrichment por registro validado

Para cada `validated_dict`:

```python
enrichment_result = enrichment_engine.run(validated_dict)
```

## 6. Mantener separado el dato original del enriquecido

El resultado devuelve:

- `original_data`
- `enriched_fields`
- `trace`
- `applied_rules`
- `metrics`

Ejemplo:

```python
result_dict = enrichment_result.to_dict()
```

## 7. Construir payload operativo enriquecido

Solo si `ID_RESOLUTION` o ingestión necesitan visibilidad de los campos derivados:

```python
payload_for_resolution = {
    **validated_dict,
    **enrichment_result.enriched_fields,
}
```

## 8. No cambiar semantic_key ni validaciones previas

No debes:

- mover esta lógica a DVL
- usar campos enriquecidos para `semantic_key`
- reabrir decisiones de validación ya cerradas

## 9. Ejecutar tests

Desde la raíz del repo:

```bash
pytest tests/unit/catalogo/enrichment -q
```

O toda la suite:

```bash
pytest -q
```

## 10. Validación funcional recomendada

Prueba con un registro real como:

```python
{
    "version_name": "1.0 MPI 80CV Reference",
    "gearbox_label": "5 Velocidades",
    "boot_capacity_l": 267,
    "production_end_year": None,
}
```

Deberías obtener:

- `gearbox_type = "manual"`
- `boot_capacity_min_l = 267`
- `boot_capacity_max_l = 267`
- `trim = "Reference"`
- `is_current_generation = True`

## 11. Integración progresiva recomendada

Orden sugerido:

1. copiar código
2. pasar tests unitarios
3. integrar en pipeline local
4. ejecutar lote de muestra
5. inspeccionar `trace`
6. validar que no se modifica input
7. versionar en GitHub

## 12. Commit sugerido

```bash
git checkout -b feature/semantic-enrichment-layer
git add src/catalogo/enrichment tests/unit/catalogo/enrichment
git commit -m "Add semantic enrichment layer for validated catalog data"
```
