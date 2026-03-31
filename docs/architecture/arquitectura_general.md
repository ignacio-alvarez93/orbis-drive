# Arquitectura general de Orbis Drive

Arquitectura base del sistema:

SCRAPERS → DICT LIMPIO → IIG → DVL → PIPELINE → BASE DE DATOS → ANALÍTICA

## Principios

- separación de responsabilidades
- trazabilidad completa
- robustez sobre velocidad
- mejor NULL que dato incorrecto

## Separación estructural

- `src/catalogo/` contiene el sistema de catálogo
- `src/mercado/` contiene el sistema de mercado

Catálogo y Mercado no comparten pipeline.
