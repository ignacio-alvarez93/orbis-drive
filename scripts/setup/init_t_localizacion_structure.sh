mkdir -p scripts/setup
nano scripts/setup/init_t_localizacion_structure.sh#!/usr/bin/env bash
set -euo pipefail

# =========================================================
# ORBIS DRIVE — Bootstrap estructura T_Localizacion
# Ejecutar desde la raíz del repo
# =========================================================

echo ">> Creando estructura de localización..."

# ---------------------------------------------------------
# DATA / TRUTH
# ---------------------------------------------------------
mkdir -p data/truth/localizacion/espana/raw
mkdir -p data/truth/localizacion/espana/staged
mkdir -p data/truth/localizacion/espana/validated

# README de localización
cat > data/truth/localizacion/README.md <<'EOF'
# T_Localizacion — Datos fuente controlados

Este directorio contiene las fuentes controladas de ingestión del pilar de localización.

## Estructura

- `espana/raw/` → CSV fuente oficial para ingestión
- `espana/staged/` → artefactos intermedios preparados para validación
- `espana/validated/` → outputs validados previos a ingestión

## Principio

Estos datos forman parte de la verdad operativa del sistema territorial.
No son legacy ni descargas externas temporales.
EOF

# Placeholders
touch data/truth/localizacion/espana/staged/.gitkeep
touch data/truth/localizacion/espana/validated/.gitkeep

# CSV canónicos
touch data/truth/localizacion/espana/raw/paises_es.csv
touch data/truth/localizacion/espana/raw/subdivisiones_es_ccaa_provincias.csv
touch data/truth/localizacion/espana/raw/localidades_es_municipios.csv

# ---------------------------------------------------------
# DATA / SAMPLES / OUTPUT
# ---------------------------------------------------------
mkdir -p data/samples/output/.gitkeep_localizacion
rm -f data/samples/output/.gitkeep_localizacion 2>/dev/null || true

# Plantilla documental para futuras ejecuciones
cat > data/samples/output/README_LOCALIZACION.md <<'EOF'
# Outputs de ejecución — T_Localizacion

Las ejecuciones del pipeline territorial deben crear carpetas con formato:

`localizacion_pipeline_YYYYMMDD_HHMMSS/`

Contenido esperado:

- `checkpoints/`
- `errors/`
- `localizacion_iig_ok.json`
- `localizacion_dvl_ok.json`
- `localizacion_batch_ok.json`
- `localizacion_ingestables.json`
- `localizacion_resuelto.json`
- `localizacion_ingestion_report.json`
EOF

# ---------------------------------------------------------
# LEGACY
# ---------------------------------------------------------
mkdir -p legacy/localizacion/mercado_ibiza
touch legacy/localizacion/mercado_ibiza/.gitkeep

# ---------------------------------------------------------
# CONTRACTS
# ---------------------------------------------------------
mkdir -p contracts/localizacion

cat > contracts/localizacion/README.md <<'EOF'
# Contratos — T_Localizacion

Contratos formales de datos del pilar territorial.

## Archivos esperados

- `t_paises.contract.json`
- `t_subdivisiones_administrativas.contract.json`
- `t_localidades.contract.json`
EOF

touch contracts/localizacion/t_paises.contract.json
touch contracts/localizacion/t_subdivisiones_administrativas.contract.json
touch contracts/localizacion/t_localidades.contract.json

# ---------------------------------------------------------
# DOCS / INGESTION
# ---------------------------------------------------------
mkdir -p docs/ingestion/t_localizacion

cat > docs/ingestion/t_localizacion/flujo_ingestion_t_localizacion.md <<'EOF'
# Flujo de ingestión — T_Localizacion

Pendiente de implementación documental.

Flujo previsto:

CSV
→ STAGING
→ IIG_Localizacion
→ DVL_Localizacion
→ Validación de lote territorial
→ Ingestión
→ Reporte
EOF

# ---------------------------------------------------------
# SCRIPTS
# ---------------------------------------------------------
mkdir -p scripts/ingestion
mkdir -p scripts/validation

touch scripts/ingestion/run_localizacion_ingestion.py
touch scripts/validation/run_iig_localizacion.py
touch scripts/validation/run_dvl_localizacion.py
touch scripts/validation/run_lote_localizacion.py

# ---------------------------------------------------------
# SRC
# ---------------------------------------------------------
mkdir -p src/localizacion/iig
mkdir -p src/localizacion/dvl
mkdir -p src/localizacion/loaders
mkdir -p src/localizacion/pipeline
mkdir -p src/localizacion/validacion_lote

mkdir -p src/localizacion/models

touch src/localizacion/__init__.py
touch src/localizacion/iig/__init__.py
touch src/localizacion/dvl/__init__.py
touch src/localizacion/loaders/__init__.py
touch src/localizacion/pipeline/__init__.py
touch src/localizacion/validacion_lote/__init__.py
touch src/localizacion/models/__init__.py

touch src/localizacion/iig/iig_localizacion.py
touch src/localizacion/dvl/dvl_localizacion.py
touch src/localizacion/loaders/localizacion_loader.py
touch src/localizacion/pipeline/localizacion_pipeline.py
touch src/localizacion/validacion_lote/lote_localizacion.py

# ---------------------------------------------------------
# TESTS
# ---------------------------------------------------------
mkdir -p tests/unit/localizacion
mkdir -p tests/integration/localizacion
mkdir -p tests/fixtures/localizacion

touch tests/unit/localizacion/__init__.py
touch tests/unit/localizacion/test_iig_localizacion.py
touch tests/unit/localizacion/test_dvl_localizacion.py
touch tests/unit/localizacion/test_lote_localizacion.py

touch tests/integration/localizacion/.gitkeep
touch tests/fixtures/localizacion/.gitkeep

echo ">> Estructura creada correctamente."
echo ">> Siguiente paso: mover/renombrar CSV reales a data/truth/localizacion/espana/raw/"
