# Scraper semimanual de versiones

## Ubicación

`src/catalogo/scraping/versiones/`

## Función

Primera capa del flujo oficial del sistema catálogo:

SCRAPER → DICT LIMPIO → IIG → DVL → VALIDACIÓN DE LOTE → INGESTIÓN

## Naturaleza

Este scraper no construye la verdad del sistema.

Solo extrae datos para ser validados posteriormente.

## Componentes

- `scraper_versiones.py` → navegación y captura HTML
- `parser_versiones.py` → parsing y extracción de campos
- `checkpoints.py` → reanudación y control de progreso
- `config.py` → configuración técnica
- `run_scraper_versiones.py` → ejecución reproducible

## Flujo semimanual

1. leer CSV de links
2. abrir navegador
3. cargar ficha
4. esperar señal humana si procede
5. capturar HTML
6. parsear HTML
7. construir dict bruto
8. guardar progreso

## Limitaciones

- no llama a IIG
- no llama a DVL
- no inserta en DB
- no debe inferir valores