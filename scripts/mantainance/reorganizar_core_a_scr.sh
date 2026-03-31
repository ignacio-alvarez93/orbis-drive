#!/usr/bin/env bash

set -e

echo "=============================="
echo " REORGANIZACION CORE → SRC"
echo "=============================="

# 1. Crear estructura destino
echo "==> Creando estructura..."

mkdir -p src/common/lifecycle
mkdir -p src/common/orchestration
mkdir -p src/catalogo/dvl
mkdir -p src/catalogo/iig
mkdir -p src/catalogo/pipeline
mkdir -p src/catalogo/scraping/shared
mkdir -p src/catalogo/scraping/sources
mkdir -p src/mercado

# 2. Función segura de movimiento
move_contents() {
  FROM="$1"
  TO="$2"

  if [ -d "$FROM" ]; then
    echo "==> Moviendo: $FROM → $TO"

    # mover archivos normales
    mv "$FROM"/* "$TO"/ 2>/dev/null || true

    # mover archivos ocultos (.xxx)
    mv "$FROM"/.[!.]* "$TO"/ 2>/dev/null || true

  else
    echo "--> No existe: $FROM (skip)"
  fi
}

# 3. Movimientos

move_contents "core/common" "src/common"
move_contents "core/lifecycle" "src/common/lifecycle"
move_contents "core/orchestration" "src/common/orchestration"

move_contents "core/dvl" "src/catalogo/dvl"
move_contents "core/iig" "src/catalogo/iig"
move_contents "core/pipeline" "src/catalogo/pipeline"

move_contents "core/scraping/shared" "src/catalogo/scraping/shared"
move_contents "core/scraping/sources" "src/catalogo/scraping/sources"

# 4. Limpieza de carpetas vacías
echo "==> Limpiando core..."

find core -type d -empty -delete 2>/dev/null || true

# eliminar core si está vacío
if [ -d "core" ]; then
  if [ -z "$(ls -A core 2>/dev/null)" ]; then
    rmdir core
    echo "==> Carpeta core eliminada"
  else
    echo "⚠️ core NO está vacía. Revisar manualmente."
  fi
fi

echo "=============================="
echo " REORGANIZACION COMPLETADA"
echo "=============================="