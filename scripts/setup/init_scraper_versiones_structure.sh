#!/usr/bin/env bash
set -e

echo "======================================"
echo " CREANDO ESTRUCTURA SCRAPER VERSIONES"
echo "======================================"

# Código fuente
mkdir -p src/catalogo/scraping/versiones

# Script ejecutable
mkdir -p scripts/scraping

# Datos de muestra
mkdir -p data/samples/input
mkdir -p data/samples/output

# Documentación
mkdir -p docs/architecture

# Archivos base del scraper
touch src/catalogo/scraping/versiones/__init__.py
touch src/catalogo/scraping/versiones/scraper_versiones.py
touch src/catalogo/scraping/versiones/parser_versiones.py
touch src/catalogo/scraping/versiones/checkpoints.py
touch src/catalogo/scraping/versiones/config.py
touch src/catalogo/scraping/versiones/README.md

# Script de ejecución
touch scripts/scraping/run_scraper_versiones.py

# Documentación técnica
touch docs/architecture/scraper_versiones.md

# Muestras de salida
touch data/samples/output/raw_version_dicts.json
touch data/samples/output/clean_version_dicts.json

# requirements si no existe
touch requirements.txt

echo "==> Estructura de scraper creada correctamente"
echo "======================================"