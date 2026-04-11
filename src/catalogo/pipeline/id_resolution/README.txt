Sustituye src/catalogo/pipeline/id_resolution/id_resolver.py por este archivo.
Este ajuste corrige build_version_id para no generar separadores vacíos.

Después ejecuta:
pytest tests/unit/catalogo/test_id_resolver.py -q
pytest -q
