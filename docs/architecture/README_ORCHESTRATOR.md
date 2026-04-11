
Orquestador central de Orbis Drive.

Archivos incluidos:
- scripts/orchestrator/run_orbis.py

Uso:
    PYTHONPATH=. python scripts/orchestrator/run_orbis.py

Flujo soportado:
- Catálogo: scraping -> IIG -> DVL/clasificación -> lote -> batch_status -> ID_RESOLUTION -> ingestión
- Mercado: placeholder
- Gestión de modelos: registro de nuevos modelos sin tocar código

Notas:
- Requiere que ya existan los runners de validación/ingestión en el repo.
- Mantiene separación estricta entre catálogo y mercado.
