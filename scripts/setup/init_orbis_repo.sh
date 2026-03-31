#!/usr/bin/env bash

set -e

echo "=============================="
echo " CREANDO ESTRUCTURA ORBIS DRIVE"
echo "=============================="

# ROOT FILES
touch README.md
touch .gitignore

# DOCS
mkdir -p docs/manifesto
mkdir -p docs/governance/resoluciones
mkdir -p docs/architecture
mkdir -p docs/ingestion/t_versiones

# DB
mkdir -p db/schema
mkdir -p db/migrations
mkdir -p db/seeds
mkdir -p db/docs

# CONTRACTS
mkdir -p contracts/catalogo
mkdir -p contracts/mercado

# SRC
mkdir -p src/common
mkdir -p src/catalogo/dvl
mkdir -p src/catalogo/iig
mkdir -p src/catalogo/pipeline
mkdir -p src/catalogo/scraping/shared
mkdir -p src/catalogo/scraping/sources
mkdir -p src/catalogo/validacion_lote
mkdir -p src/catalogo/loaders
mkdir -p src/mercado
mkdir -p src/analytics

# DATA
mkdir -p data/truth
mkdir -p data/samples
mkdir -p data/external

# TESTS
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/contracts
mkdir -p tests/fixtures

# SCRIPTS
mkdir -p scripts/setup
mkdir -p scripts/validation
mkdir -p scripts/maintenance

# LEGACY
mkdir -p legacy

echo "==> Estructura creada correctamente"
echo "=============================="
