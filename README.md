# Orbis Drive

Orbis Drive es una plataforma de inteligencia de mercado automovilístico con alcance España-UE y proyección multipaís.

## Principios del sistema

- Separación de responsabilidades
- Mejor NULL que dato incorrecto
- Trazabilidad completa
- Robustez sobre velocidad
- GitHub como fuente única de verdad estructural

## Arquitectura base

SCRAPERS → DICT LIMPIO → IIG → DVL → PIPELINE → BASE DE DATOS → ANALÍTICA

## Separación estructural obligatoria

- `src/catalogo/` → sistema de catálogo
- `src/mercado/` → sistema de mercado

Catálogo y Mercado no comparten pipeline operativo.

## Estructura principal

- `docs/` → gobierno, arquitectura, resoluciones y flujos
- `db/` → esquema SQL, migraciones, seeds y documentación relacional
- `contracts/` → contratos formales de datos
- `src/` → código fuente
- `data/` → datos ligeros versionables
- `tests/` → pruebas
- `scripts/` → utilidades operativas
- `legacy/` → material retirado o heredado
