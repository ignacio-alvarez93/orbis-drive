
---

## `docs/architecture/localizacion/flujo_validacion_localizacion.md`

```md
# Flujo de validación — T_Localizacion

## Proyecto
Orbis Drive

## Estado
Diseño operativo inicial

## Objetivo

Definir el flujo oficial de validación e ingestión de `T_Localizacion` para que la carga territorial siga la misma disciplina sistémica aplicada en `T_Versiones`:

- ingreso por CSV controlado
- validación estructural previa
- validación semántica previa
- validación global de lote
- ingestión controlada
- trazabilidad completa por ejecución

Este enfoque se alinea con el principio fundacional de Orbis Drive: el dato no entra por confianza, entra por verificación formal. 

---

# 1. Flujo oficial propuesto

El flujo de localización se define como:

```text
CSV
→ STAGING
→ IIG_Localizacion
→ DVL_Localizacion
→ VALIDACION_LOTE_Localizacion
→ INGESTION
→ REPORTE