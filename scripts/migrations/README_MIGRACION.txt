MIGRACIÓN COMPLETA T_VERSIONES -> UNIQUE V2

Este paquete alinea persistencia con semantic_key_v2.

Incluye:
- t_versiones_loader.py
- migrate_t_versiones_unique_v2.py
- migrate_t_versiones_unique_v2.sql

1) Sustituir loader
Ruta destino:
src/catalogo/loaders/t_versiones_loader.py

2) Ejecutar migración SQLite
Comando recomendado:
PYTHONPATH=. python scripts/migrations/migrate_t_versiones_unique_v2.py --db-path db/local/Orbis_Drive.db

3) Reejecutar León
Orden recomendado:
- mark_batch_passed
- run_t_versiones_id_resolution
- run_t_versiones_ingestion

4) Resultado esperado
Las versiones de León que antes quedaban como:
(version_name_canonical, generation_id) duplicado
deben pasar a insertarse como distintas si cambian:
- production_start_year
- production_end_year
