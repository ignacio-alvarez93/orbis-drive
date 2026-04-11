# RESOLUCIÓN DE DIRECCIÓN GENERAL

## Consolidación global de identidad semántica de versión y evolución del modelo de catálogo

**Proyecto:** Orbis Drive
**Fecha:** Abril 2026
**Estado:** 🚀 APROBADO — ESTÁNDAR GLOBAL DEL SISTEMA

---

# 1. RESUMEN EJECUTIVO

Dirección General aprueba la consolidación definitiva de la nueva definición de identidad semántica de versión (`semantic_key_v2`) como estándar global del sistema Orbis Drive.

Asimismo, se establece la evolución controlada del modelo de catálogo para dar cobertura a vehículos sin generación identificable.

---

# 2. ESTADO ACTUAL DEL SISTEMA

Se declara completada la ingestión de los siguientes modelos:

* ✅ SEAT Ibiza → INGESTIÓN COMPLETA
* ✅ SEAT León → INGESTIÓN COMPLETA

El sistema ha demostrado:

* ingestión controlada real
* validación estructural y semántica robusta
* eliminación de duplicados sin pérdida de información
* representación completa de modelos complejos

---

# 3. PROBLEMA IDENTIFICADO

La definición anterior de identidad semántica:

```text
manufacturer + model + generation + version_name
```

provocaba:

* colapso de versiones reales
* falsos duplicados
* conflictos en validación de lote
* pérdida silenciosa de información

---

# 4. DECISIÓN — IDENTIDAD SEMÁNTICA

Se establece como definición oficial y obligatoria:

## semantic_key_v2

```text
manufacturer
+ model
+ generation
+ version_name
+ production_start_year
+ production_end_year
```

---

# 5. ALCANCE DEL CAMBIO

El cambio se aplica de forma transversal a TODO el sistema:

* VALIDACIÓN DE LOTE
* ID_RESOLUTION
* INGESTIÓN
* BASE DE DATOS (`T_Versiones`)
* ORQUESTADOR

El orquestador existente queda validado y alineado con este estándar.

---

# 6. PRINCIPIOS PRESERVADOS

La nueva definición:

✔ no introduce inferencia
✔ no modifica datos
✔ utiliza únicamente información explícita
✔ mantiene trazabilidad completa

Se mantiene el principio:

👉 T_Versiones = tabla de verdad semántica del vehículo

---

# 7. RESULTADOS VALIDADOS

## SEAT Ibiza

* consolidación semántica correcta
* eliminación de duplicados
* ratio ≈ 91,7%

## SEAT León

* cobertura completa (100%)
* duplicados: 0
* conflictos: 0
* diferenciación correcta de variantes

---

# 8. EVOLUCIÓN DEL MODELO — VEHÍCULOS SIN GENERACIÓN

Se reconoce que una parte del mercado presenta:

* ausencia de generación identificable
* estructuras incompletas en fuente
* modelos históricos o no normalizados

---

## 8.1 DECISIÓN

Se aprueba la creación de una nueva tabla:

👉 **T_Versiones_Sin_Generacion**

---

## 8.2 DEFINICIÓN

Esta tabla será:

✔ estructuralmente idéntica a `T_Versiones`
✔ alineada con el mismo contrato de datos
✔ sujeta a las mismas capas de validación

Diferencia:

👉 `generation_id` no será obligatorio

---

## 8.3 PRINCIPIOS

Se establece:

* no se forzará generación artificial
* no se inferirá jerarquía inexistente
* se mantendrá la integridad semántica

---

## 8.4 OBJETIVO

Permitir:

* ampliar cobertura del catálogo
* capturar realidad del mercado
* mantener coherencia del sistema

---

# 9. IMPACTO EN EL SISTEMA

Este doble avance:

### 9.1 semantic_key_v2

permite:

* representación precisa de variantes
* eliminación de colisiones de identidad

### 9.2 T_Versiones_Sin_Generacion

permite:

* cubrir casos reales no estructurados
* evitar pérdida de información válida

---

# 10. CAMBIO DE NIVEL DEL SISTEMA

Se establece oficialmente:

👉 Orbis Drive pasa de sistema funcional
a sistema semánticamente completo

Capaz de:

* representar evolución temporal
* manejar excepciones estructurales
* escalar sin pérdida de verdad

---

# 11. ESTADO DEL SISTEMA

Se declara:

* catálogo estable
* identidad semántica consolidada
* ingestión operativa real
* orquestador funcional
* sistema preparado para escalado

---

# 12. SIGUIENTE FASE AUTORIZADA

Se autoriza iniciar:

## 12.1 Escalado de catálogo

* nuevos modelos
* nuevos fabricantes

## 12.2 Implementación de T_Versiones_Sin_Generacion

## 12.3 Desarrollo del modelo territorial multipaís

## 12.4 Integración con sistema de mercado

---

# 13. PRINCIPIO CONSOLIDADO

Se refuerza como norma del sistema:

👉 la verdad del catálogo depende de cómo se define la identidad

y de:

👉 respetar la realidad del dato, incluso cuando es incompleta

---

# 14. MENSAJE FINAL

“El sistema no solo ha aprendido a diferenciar versiones…

ahora también ha aprendido a aceptar cuando la realidad no encaja en una estructura perfecta.”

---

# RESOLUCIÓN FINAL

✅ semantic_key_v2 ESTABLECIDO COMO ESTÁNDAR GLOBAL
✅ SEAT IBIZA Y SEAT LEÓN COMPLETAMENTE INGESTADOS
✅ EXTENSIÓN DEL MODELO PARA CASOS SIN GENERACIÓN APROBADA
🚀 ORBIS DRIVE PREPARADO PARA ESCALAR CON PRECISIÓN Y COBERTURA

---

**Dirección General**
Proyecto Orbis Drive
