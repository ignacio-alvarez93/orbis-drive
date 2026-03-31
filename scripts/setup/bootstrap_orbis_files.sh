#!/usr/bin/env bash
set -e

echo "=============================="
echo " BOOTSTRAP ARCHIVOS BASE ORBIS"
echo "=============================="

# README raíz
cat > README.md <<'EOF'
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
EOF

# .gitignore
cat > .gitignore <<'EOF'
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.venv/
venv/
env/

# Environment
.env
.env.*
*.secret

# Databases
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/
*.out

# OS / Editor
.DS_Store
Thumbs.db
.vscode/
.idea/

# Jupyter
.ipynb_checkpoints/

# Build / cache
.cache/
dist/
build/
*.egg-info/

# Temporary data
tmp/
temp/
outputs/
exports/
downloads/

# Large raw datasets
data/raw/
data/tmp/
data/cache/

# Test / coverage
.coverage
htmlcov/
.pytest_cache/

# Misc
*.bak
*.swp
EOF

# Normas repo
cat > docs/governance/normas_repositorio.md <<'EOF'
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
EOF

# Arquitectura general
cat > docs/architecture/arquitectura_general.md <<'EOF'
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
EOF

# Flujo T_Versiones
cat > docs/ingestion/t_versiones/flujo_ingestion_t_versiones.md <<'EOF'
# Flujo de ingestión de T_Versiones

Flujo oficial aprobado:

SCRAPER
↓
DICT LIMPIO (CONTRATO 1:1 DB)
↓
IIG (CONTROL ESTRUCTURAL)
↓
DVL (VALIDACIÓN SEMÁNTICA)
↓
VALIDACIÓN DE LOTE
↓
INGESTIÓN

## Principio rector

T_Versiones no se carga por confianza.
T_Versiones se carga por verificación formal.
EOF

# DB schema README
cat > db/schema/README.md <<'EOF'
# Esquema SQL de Orbis Drive

Esta carpeta contiene el esquema SQL oficial versionado del sistema.

## Principios

- el SQL aquí almacenado es versionable y trazable
- la base SQLite operativa no se sube a GitHub
- toda modificación estructural debe reflejarse mediante migraciones controladas

## Regla operativa

No almacenar aquí dumps de base de datos.
Solo definición estructural y artefactos SQL oficiales del sistema.
EOF

# Contracts README
cat > contracts/README.md <<'EOF'
# Contratos de datos de Orbis Drive

Esta carpeta contiene los contratos formales del sistema.

- `contracts/catalogo/` → contratos del sistema catálogo
- `contracts/mercado/` → contratos del sistema mercado

Los contratos son la referencia operativa del dato.
EOF

# Contrato mínimo T_Versiones
cat > contracts/catalogo/t_versiones.contract.json <<'EOF'
{
  "contract_name": "t_versiones",
  "domain": "catalogo",
  "description": "Contrato oficial de datos para T_Versiones. Referencia estructural para IIG_Catalogo.",
  "status": "approved",
  "strict_mode": true,
  "additional_properties": false,
  "fields": {}
}
EOF

# READMEs mínimos opcionales
touch docs/governance/resoluciones/.gitkeep
touch db/migrations/.gitkeep
touch db/seeds/.gitkeep
touch db/docs/.gitkeep
touch contracts/mercado/.gitkeep
touch data/truth/.gitkeep
touch data/samples/.gitkeep
touch data/external/.gitkeep
touch tests/unit/.gitkeep
touch tests/integration/.gitkeep
touch tests/contracts/.gitkeep
touch tests/fixtures/.gitkeep
touch scripts/validation/.gitkeep
touch scripts/maintenance/.gitkeep
touch legacy/.gitkeep

echo "==> Archivos base creados"
echo "=============================="