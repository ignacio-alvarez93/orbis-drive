#!/usr/bin/env bash
set -e

echo "======================================"
echo " CREANDO ESTRUCTURA SCRAPER VERSIONES V3"
echo "======================================"

# Código fuente
mkdir -p src/catalogo/scraping/versiones/v3

# Scripts
mkdir -p scripts/scraping

# Datos de muestra
mkdir -p data/samples/input/html_examples
mkdir -p data/samples/output/versiones_scraper_v3/checkpoints
mkdir -p data/samples/output/versiones_scraper_v3/errors

# Docs
mkdir -p docs/architecture

# Archivos base v3
touch src/catalogo/scraping/versiones/v3/__init__.py
touch src/catalogo/scraping/versiones/v3/runner.py
touch src/catalogo/scraping/versiones/v3/parser.py
touch src/catalogo/scraping/versiones/v3/browser_adapters.py
touch src/catalogo/scraping/versiones/v3/checkpoints.py
touch src/catalogo/scraping/versiones/v3/field_mapping.py
touch src/catalogo/scraping/versiones/v3/README.md

# Wrappers compatibles
touch src/catalogo/scraping/versiones/scraper_versiones.py
touch src/catalogo/scraping/versiones/parser_versiones.py
touch src/catalogo/scraping/versiones/checkpoints.py
touch src/catalogo/scraping/versiones/config.py

# Scripts operativos
touch scripts/scraping/run_scraper_versiones.py
touch scripts/scraping/smoke_test_scraper_versiones_v3.py

# Doc técnica
touch docs/architecture/scraper_versiones.md

echo "==> Estructura v3 creada correctamente"
echo "======================================"