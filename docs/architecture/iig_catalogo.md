# IIG_Catalogo

## Qué es

`IIG_Catalogo` es el Input Integrity Guard del sistema de catálogo de Orbis Drive.

Actúa como capa de validación estructural previa a la validación semántica.

## Flujo dentro del sistema

SCRAPER → DICT LIMPIO → IIG → DVL → VALIDACIÓN DE LOTE → INGESTIÓN

## Responsabilidades

- validar que el registro respeta el contrato formal
- validar claves extra
- validar claves requeridas y campos mínimos
- validar tipos primitivos
- validar formatos básicos de fecha y datetime
- detectar densidad alta de nulos
- generar resultados estructurados por registro y por lote

## Qué NO hace

- no normaliza
- no corrige
- no infiere
- no modifica el input

## Contrato asociado

El contrato oficial usado por `IIG_Catalogo` es:

`contracts/catalogo/t_versiones.contract.json`

## Ejemplo de uso

```python
from src.catalogo.iig.iig_catalogo import IIG_Catalogo

iig = IIG_Catalogo(
    contract_path="contracts/catalogo/t_versiones.contract.json",
    mode="observacion",
)

resultado = iig.validate_record({
    "version_id": "seat_ibiza_2021_1.0_tsi_95_style",
    "manufacturer_id": "seat",
    "model_id": "ibiza",
    "generation_id": "ibiza_kj_2021",
    "source": "encycarpedia",
    "source_version_url": "https://example.com/seat-ibiza-version",
    "manufacturer_name": "SEAT",
    "model_name": "Ibiza",
    "generation_name": "KJ 2021",
    "version_name": "1.0 TSI 95 Style",
})

print(resultado.is_valid)
print(resultado.flags)