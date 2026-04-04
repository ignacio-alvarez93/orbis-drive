# RESOLUCIÓN DE DIRECCIÓN GENERAL

## Incorporación de la capa ID_RESOLUTION al sistema de catálogo

**Proyecto:** Orbis Drive
**Fecha:** Abril 2026
**Estado:** ✅ APROBADA — INTEGRACIÓN FORMAL EN PIPELINE

---

## 1. CONTEXTO

Durante la preparación de la ingestión piloto de `T_Versiones` se ha constatado la existencia de una separación estructural entre:

* dato semánticamente válido (post IIG, DVL y validación de lote)
* dato persistible en base de datos

El dataset validado no contenía los identificadores necesarios para cumplir con el modelo físico de persistencia.

---

## 2. PROBLEMA IDENTIFICADO

El sistema de catálogo disponía de:

* validación estructural (IIG)
* validación semántica (DVL)
* validación de lote

pero carecía de una capa responsable de:

👉 resolver identidad persistible (IDs)

Esto impedía la conexión directa entre:

```text
dato validado → base de datos
```

---

## 3. DECISIÓN

Se aprueba la incorporación de una nueva capa en el pipeline:

👉 **ID_RESOLUTION**

---

## 4. FUNCIÓN DE LA CAPA

La capa **ID_RESOLUTION** es responsable de:

* resolver `manufacturer_id`
* resolver `model_id`
* resolver `generation_id`
* generar `version_name_canonical`
* generar `version_id`

A partir de:

* dataset validado semánticamente
* base de datos existente

---

## 5. PRINCIPIOS DE DISEÑO

La capa ID_RESOLUTION:

✔ no modifica el dato validado
✔ no inventa entidades inexistentes
✔ no crea jerarquía implícita
✔ falla de forma explícita si no puede resolver identidad

Esto preserva los principios del sistema:

* no inferencia
* trazabilidad completa
* separación de responsabilidades

---

## 6. NUEVO FLUJO OFICIAL

Se establece como flujo oficial del sistema catálogo:

```text
SCRAPER
→ DICT LIMPIO
→ IIG
→ DVL
→ VALIDACIÓN DE LOTE
→ ID_RESOLUTION
→ INGESTIÓN
```

---

## 7. IMPACTO

La incorporación de esta capa:

* habilita la ingestión real de `T_Versiones`
* separa claramente validación de persistencia
* garantiza integridad referencial antes de inserción

---

## 8. ESTADO

✔ Implementación completada
✔ Validación operativa realizada
✔ Integración en repositorio confirmada

---

## 9. CONCLUSIÓN

Se declara formalmente incorporada la capa:

👉 **ID_RESOLUTION**

como componente obligatorio del sistema de catálogo de Orbis Drive.

---

**Dirección General**
Proyecto Orbis Drive
