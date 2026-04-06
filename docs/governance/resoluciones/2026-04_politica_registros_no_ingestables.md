# RESOLUCIÓN DE DIRECCIÓN GENERAL

## Gestión de registros no ingestables en T_Versiones

**Proyecto:** Orbis Drive
**Fecha:** Abril 2026
**Estado:** 🚀 APROBADO — POLÍTICA OFICIAL DE GESTIÓN DE INCOMPLETITUD

---

## 1. RESUMEN EJECUTIVO

Durante la ejecución de la ingestión ampliada de `T_Versiones`, se ha detectado la existencia de registros:

👉 semánticamente válidos
👉 estructuralmente coherentes
👉 pero no ingestables

debido a la ausencia de campos críticos definidos por el sistema.

---

## 2. NATURALEZA DEL PROBLEMA

Se establece que:

👉 no todos los datos reales del mercado son inmediatamente persistibles

Motivo:

* heterogeneidad de fuentes externas
* política de validación estricta (IIG + DVL)
* principio de no inferencia

---

## 3. PRINCIPIO FUNDAMENTAL

Se refuerza:

👉 Orbis Drive prioriza la verdad del dato sobre la completitud inmediata

Esto implica:

❌ no inferir
❌ no completar artificialmente
❌ no forzar ingestión

---

## 4. CLASIFICACIÓN OFICIAL DE REGISTROS

Se aprueba el siguiente modelo de estados:

---

### ✅ INGESTABLE

Condición:

* pasa IIG
* pasa DVL
* pasa validación de lote

Acción:

👉 se inserta en `T_Versiones`

---

### 🟡 PENDIENTE_RECUPERABLE

Condición:

* versión real del mercado
* identidad coherente
* ausencia de campo crítico
* sin incoherencias

Ejemplo:

```json
fuel_type = NULL
```

Acción:

👉 no se ingesta
👉 se persiste estructuradamente
👉 se marca para enriquecimiento futuro

---

### 🔴 RECHAZADO_TECNICO

Condición:

* error de parsing
* incoherencia semántica
* datos corruptos

Acción:

👉 no se ingesta
👉 requiere corrección del sistema

---

## 5. ARQUITECTURA APROBADA

Se establece la creación de persistencia auxiliar:

```text
data/catalogo_pendientes/
```

Estructura:

* `pendientes_dvl.json`
* `rechazados_tecnicos.json`

Cada registro incluirá:

* payload completo
* causa de exclusión
* etapa del pipeline
* timestamp

---

## 6. INTEGRACIÓN EN EL PIPELINE

El flujo oficial pasa a ser:

```text
SCRAPER
→ DICT LIMPIO
→ IIG
→ DVL
→ VALIDACIÓN DE LOTE
→ CLASIFICACIÓN (INGESTABLE / PENDIENTE / RECHAZADO)
→ ID_RESOLUTION
→ INGESTIÓN
```

---

## 7. IMPACTO EN EL SISTEMA

Esta decisión habilita:

✔ conservación de datos válidos no ingestables
✔ enriquecimiento futuro multicapa
✔ ingestión progresiva sin pérdida de información
✔ separación clara entre calidad y cobertura

---

## 8. ALINEACIÓN CON EL SISTEMA

La política cumple:

* no inferencia
* trazabilidad completa
* separación de responsabilidades
* robustez sobre velocidad

---

## 9. ESTADO FINAL

Se declara:

✔ política de incompletitud definida
✔ gestión de registros no ingestables formalizada
✔ sistema preparado para enriquecimiento futuro

---

## 10. MENSAJE FINAL

“No todo dato válido puede entrar hoy…

pero ningún dato válido debe perderse.”

---

## RESOLUCIÓN FINAL

✅ MODELO DE ESTADOS APROBADO
✅ PERSISTENCIA DE PENDIENTES AUTORIZADA
🚀 SISTEMA PREPARADO PARA EVOLUCIÓN MULTIFUENTE

Dirección General
Proyecto Orbis Drive
