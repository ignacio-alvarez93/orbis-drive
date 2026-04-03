# Validación de lote de catálogo

Implementación de referencia para la capa `VALIDACIÓN DE LOTE` de Orbis Drive.

## Flujo

`SCRAPER -> DICT LIMPIO -> IIG -> DVL -> VALIDACIÓN DE LOTE -> INGESTIÓN`

## Entrada esperada

- `data/samples/input/lote_t_versiones.json`
- El campo `_scenario` se ignora por completo en la lógica productiva.

## Uso rápido

```python
from src.catalogo.validacion_lote.lote_catalogo import LoteCatalogo

resultado = LoteCatalogo().validate_file("data/samples/input/lote_t_versiones.json")
```

## Capacidades

- Duplicados semánticos por clave base.
- Conflictos internos entre registros de la misma versión.
- Conflictos internos dentro de un mismo registro.
- Outliers no bloqueantes.
- Cobertura por generación y completitud media.
- Resultado final serializable a JSON.
