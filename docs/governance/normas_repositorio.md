# Normas del repositorio de Orbis Drive

## 1. Principio rector

El repositorio GitHub de Orbis Drive es la fuente única de verdad estructural del sistema.

## 2. Separación obligatoria

- Catálogo ≠ Mercado
- Código ≠ Datos
- Documentación ≠ Contratos
- Core ≠ Legacy

## 3. Ubicación oficial

- `docs/` → manifiesto, resoluciones, arquitectura y flujos
- `db/` → SQL, migraciones, seeds ejecutables y documentación relacional
- `contracts/` → contratos formales de datos
- `src/` → código fuente
- `data/` → datos ligeros versionables
- `tests/` → pruebas
- `scripts/` → scripts operativos
- `legacy/` → material heredado o retirado

## 4. Archivos permitidos en GitHub

Se permite subir:
- documentación oficial
- SQL del esquema
- contratos JSON
- código fuente
- tests
- muestras controladas
- scripts de mantenimiento y validación

## 5. Archivos prohibidos en GitHub

No se permite subir:
- bases SQLite operativas
- dumps completos de scraping
- outputs pesados
- archivos temporales
- cachés
- logs no estructurales
- credenciales
- `.env`

## 6. Nomenclatura

### Carpetas
- minúsculas
- sin espacios
- semántica estable

### Archivos
- minúsculas
- `snake_case`
- fecha delante cuando sea documento oficial
- prefijo numérico si hay orden de ejecución

## 7. Contratos de datos

El contrato operativo del sistema vive en `contracts/`.

`contracts/catalogo/t_versiones.contract.json` es referencia oficial para `IIG_Catalogo`.
