# Scraper semimanual de versiones v3

Implementación alineada con el repositorio oficial de Orbis Drive.

## Alcance
- Extrae HTML desde CSV o desde HTML local.
- Genera `raw_dict` y `clean_dict` candidatos a validación.
- Guarda checkpoints y errores.
- No llama a IIG, DVL ni base de datos.

## Ubicación
`src/catalogo/scraping/versiones/v3/`

## Scripts
- `scripts/scraping/run_scraper_versiones.py`
- `scripts/scraping/smoke_test_scraper_versiones_v3.py`
