Sustituye este archivo en tu repo:

scripts/maintenance/reingest_t_versiones.py

Qué corrige:
- deja de contar y borrar por version_id
- cuenta y borra por la misma clave semántica que usa TVersionesLoader:
  (version_name_canonical, generation_id, production_start_year, production_end_year)

Por qué:
- los registros antiguos pueden no tener el mismo version_id
- pero sí ser duplicados semánticos para el loader
- así la reingestión realmente reemplaza el contenido anterior

Comando recomendado León:
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PYTHONPATH=. python scripts/maintenance/reingest_t_versiones.py \
--db-path db/local/Orbis_Drive.db \
--dataset data/samples/output/seat_leon_with_ids.json \
--report-path data/samples/output/reingestion_leon_report.json

Comando recomendado Ibiza:
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PYTHONPATH=. python scripts/maintenance/reingest_t_versiones.py \
--db-path db/local/Orbis_Drive.db \
--dataset data/samples/output/seat_ibiza_with_ids.json \
--report-path data/samples/output/reingestion_ibiza_report.json
