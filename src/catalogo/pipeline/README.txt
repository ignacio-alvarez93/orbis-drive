Sustituye este archivo en tu repo:

src/catalogo/pipeline/ingestion_pipeline.py

Qué corrige:
- evita transacciones anidadas
- si la conexión ya está en transacción, la pipeline no hace BEGIN/COMMIT/ROLLBACK
- mantiene compatibilidad con:
  - ejecución normal
  - reingestión controlada
  - strict_batch True/False

El problema real era:
- el script de reingestión ya abría transacción
- la pipeline también abría transacción
- eso provocaba una excepción interna y, con strict_batch=False, devolvía un reporte vacío

Después:
pytest -q

Y luego:
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PYTHONPATH=. python scripts/maintenance/reingest_t_versiones.py \
--db-path db/local/Orbis_Drive.db \
--dataset data/samples/output/seat_leon_with_ids.json \
--report-path data/samples/output/reingestion_leon_report.json
