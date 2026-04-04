
# ID Resolution para T_Versiones

## Objetivo

Convertir un dataset ya validado por:

- IIG_Catalogo
- DVL_Catalogo
- Validación de lote

en un dataset **ingestable** por la SQLite actual de Orbis Drive.

## Problema que resuelve

El dataset piloto validado contiene identidad semántica:

- manufacturer_name
- model_name
- generation_name
- version_name

pero la base exige identidad persistible:

- manufacturer_id
- model_id
- generation_id
- version_id

Además, `T_Versiones.generation_id` es obligatorio y la tabla impone unicidad por
`(version_name_canonical, generation_id)`.

## Reglas

1. No crear fabricantes, modelos o generaciones en esta fase.
2. Reutilizar exclusivamente IDs ya existentes en DB.
3. Generar `version_name_canonical` de forma determinista.
4. Generar `version_id` de forma determinista.
5. Si una referencia jerárquica no existe, el registro no es ingestable.

## Flujo

```text
DATASET VALIDADO
    ↓
ID RESOLUTION
    ↓
DATASET INGESTABLE
    ↓
INGESTIÓN EN DB
```

## Ejecución

```bash
PYTHONPATH=. python scripts/ingestion/run_t_versiones_id_resolution.py       --db-path db/local/orbis_drive.sqlite       --input data/samples/input/lote_t_versiones_pilot_validado.json       --output data/samples/output/lote_t_versiones_pilot_resuelto.json
```
