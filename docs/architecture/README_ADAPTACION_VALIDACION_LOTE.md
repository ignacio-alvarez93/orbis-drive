# Adaptación de VALIDACIÓN DE LOTE

## Objetivo
Alinear la validación de lote con la definición oficial de "Versión" aprobada por Dirección General:

- duplicado = misma identidad semántica completa
- variante válida = misma base pero distinto periodo explícito
- conflicto = misma base + mismo periodo (o sin diferenciación temporal suficiente) + contradicción técnica

## Cambios incluidos
- `semantic_key_v2.py`
  - añade `build_base_version_key`
  - añade `build_conflict_key`
  - añade `build_variant_key`
  - `build_semantic_key_v2` pasa a ser alias de variante oficial
- `duplicates.py`
  - agrupa por `build_duplicate_key`
- `conflicts.py`
  - reagrupa por `build_conflict_key`
  - detecta conflicto aunque `semantic_key_v2` haya separado variantes por fallback
- `lote_validator.py`
  - usa `detect_group_conflicts(records)` en vez de reutilizar la agrupación de duplicados
- tests nuevos de regresión

## Pasos
1. Copia los archivos del ZIP a tu repo respetando rutas.
2. Ejecuta:
   `pytest tests/unit/catalogo/validacion_lote/test_lote_validator.py -q`
3. Después:
   `pytest -q`
