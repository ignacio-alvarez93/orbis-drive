Sustituye tu archivo actual por este:
src/catalogo/pipeline/id_resolution/id_resolver.py

Después ejecuta:
pytest tests/unit/catalogo/test_id_resolver.py -q
pytest -q

Si sigue fallando, el problema ya no será el alias sino la ruta o la caché.
En ese caso ejecuta también:
find . -type d -name __pycache__ -exec rm -rf {} +
pytest tests/unit/catalogo/test_id_resolver.py -q
