Sustituye este archivo en tu repo:

src/catalogo/enrichment/core/enrichment_engine.py

Qué corrige:
- compatibilidad con reglas ESL v1 que devuelven:
  {campo: {"value": ..., "source": ..., "rule": ...}}
- compatibilidad con reglas ESL v1 que devuelven:
  {campo: valor}
- compatibilidad con reglas ESL v2:
  rule(data, result)

Después ejecuta:
pytest tests/unit/catalogo/enrichment -q
pytest -q
