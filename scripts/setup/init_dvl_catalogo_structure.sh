#!/usr/bin/env bash
set -e

echo "======================================"
echo " CREANDO ESTRUCTURA DVL_CATALOGO"
echo "======================================"

# 1. Estructura de código
mkdir -p src/catalogo/dvl/core
mkdir -p src/catalogo/dvl/rules
mkdir -p src/catalogo/dvl/enums
mkdir -p src/catalogo/dvl/metrics

# 2. Estructura de tests
mkdir -p tests/unit/catalogo/dvl

# 3. Documentación técnica
mkdir -p docs/architecture

# 4. Archivos base python para paquetes
touch src/catalogo/dvl/__init__.py
touch src/catalogo/dvl/core/__init__.py
touch src/catalogo/dvl/rules/__init__.py
touch src/catalogo/dvl/enums/__init__.py
touch src/catalogo/dvl/metrics/__init__.py
touch tests/unit/catalogo/dvl/__init__.py

# 5. Archivo principal del módulo si aún no existe
touch src/catalogo/dvl/dvl_catalogo.py

# 6. Test principal si aún no existe
touch tests/unit/catalogo/dvl/test_dvl_catalogo.py

# 7. Documento técnico si aún no existe
touch docs/architecture/dvl_catalogo.md

echo "==> Estructura DVL_Catalogo creada correctamente"
echo ""
echo "Rutas preparadas:"
echo " - src/catalogo/dvl/"
echo " - tests/unit/catalogo/dvl/"
echo " - docs/architecture/dvl_catalogo.md"
echo "======================================"