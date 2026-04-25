#!/usr/bin/env bash
set -euo pipefail

# Ejecutar desde la raíz del repositorio orbis-drive

echo "Creando estructura base de T_Concesionarios..."

mkdir -p \
  src/catalogo/concesionarios/models \
  src/catalogo/concesionarios/staging \
  src/catalogo/concesionarios/iig \
  src/catalogo/concesionarios/normalization \
  src/catalogo/concesionarios/dvl/rules \
  src/catalogo/concesionarios/validacion_lote/rules \
  src/catalogo/concesionarios/enrichment/rules \
  src/catalogo/concesionarios/id_resolution \
  src/catalogo/concesionarios/pipeline \
  contracts/catalogo \
  db/schema \
  docs/architecture \
  scripts/ingestion \
  tests/unit/catalogo/concesionarios \
  tests/integration/catalogo/concesionarios \
  data/samples/concesionarios \
  data/samples/output \
  data/concesionarios_pendientes

touch \
  src/catalogo/concesionarios/__init__.py \
  src/catalogo/concesionarios/models/__init__.py \
  src/catalogo/concesionarios/models/concesionario_raw_record.py \
  src/catalogo/concesionarios/models/concesionario_normalized.py \
  src/catalogo/concesionarios/models/concesionario_validated.py \
  src/catalogo/concesionarios/models/concesionario_resolved.py \
  src/catalogo/concesionarios/models/pipeline_result.py \
  src/catalogo/concesionarios/staging/__init__.py \
  src/catalogo/concesionarios/staging/staging_loader.py \
  src/catalogo/concesionarios/iig/__init__.py \
  src/catalogo/concesionarios/iig/iig_concesionarios.py \
  src/catalogo/concesionarios/normalization/__init__.py \
  src/catalogo/concesionarios/normalization/canonicalizers.py \
  src/catalogo/concesionarios/normalization/contact_utils.py \
  src/catalogo/concesionarios/normalization/location_prep.py \
  src/catalogo/concesionarios/normalization/normalization_concesionarios.py \
  src/catalogo/concesionarios/dvl/__init__.py \
  src/catalogo/concesionarios/dvl/rules/__init__.py \
  src/catalogo/concesionarios/dvl/rules/identity_rules.py \
  src/catalogo/concesionarios/dvl/rules/contact_rules.py \
  src/catalogo/concesionarios/dvl/rules/commercial_actor_rules.py \
  src/catalogo/concesionarios/dvl/dvl_concesionarios.py \
  src/catalogo/concesionarios/validacion_lote/__init__.py \
  src/catalogo/concesionarios/validacion_lote/rules/__init__.py \
  src/catalogo/concesionarios/validacion_lote/rules/duplicates.py \
  src/catalogo/concesionarios/validacion_lote/rules/conflicts.py \
  src/catalogo/concesionarios/validacion_lote/validacion_lote_concesionarios.py \
  src/catalogo/concesionarios/enrichment/__init__.py \
  src/catalogo/concesionarios/enrichment/enrichment_engine.py \
  src/catalogo/concesionarios/enrichment/rules/__init__.py \
  src/catalogo/concesionarios/enrichment/rules/domains.py \
  src/catalogo/concesionarios/enrichment/rules/handles.py \
  src/catalogo/concesionarios/enrichment/rules/quality_flags.py \
  src/catalogo/concesionarios/id_resolution/__init__.py \
  src/catalogo/concesionarios/id_resolution/semantic_key.py \
  src/catalogo/concesionarios/id_resolution/location_resolver_adapter.py \
  src/catalogo/concesionarios/id_resolution/id_resolution_concesionarios.py \
  src/catalogo/concesionarios/pipeline/__init__.py \
  src/catalogo/concesionarios/pipeline/ingestion_pipeline.py \
  contracts/catalogo/t_concesionarios.contract.json \
  db/schema/010_t_concesionarios.sql \
  docs/architecture/t_concesionarios.md \
  scripts/ingestion/run_t_concesionarios_ingestion.py \
  tests/unit/catalogo/concesionarios/test_iig_concesionarios.py \
  tests/unit/catalogo/concesionarios/test_normalization_concesionarios.py \
  tests/unit/catalogo/concesionarios/test_dvl_concesionarios.py \
  tests/unit/catalogo/concesionarios/test_semantic_key.py \
  tests/integration/catalogo/concesionarios/test_ingestion_pipeline.py \
  data/samples/concesionarios/concesionarios_autocasion_cochesnet_sample.json

echo "Estructura creada correctamente."