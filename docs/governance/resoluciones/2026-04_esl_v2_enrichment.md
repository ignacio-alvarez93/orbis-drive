# RESOLUCIÓN DE DIRECCIÓN GENERAL

## Implementación de la Capa de Enriquecimiento Semántico v2 (ESL v2)

**Proyecto:** Orbis Drive
**Fecha:** Abril 2026
**Estado:** 🚀 APROBADO — EVOLUCIÓN ANALÍTICA DEL SISTEMA

---

# 1. RESUMEN EJECUTIVO

Tras la finalización de la ingestión completa de:

* SEAT Ibiza
* SEAT León

y la consolidación del sistema catálogo como sistema operativo, se aprueba la evolución hacia una nueva capacidad:

👉 **enriquecimiento semántico determinista del dato**

---

# 2. CONTEXTO DEL SISTEMA

El sistema actual ejecuta de forma estable:

```text
SCRAPER → DICT LIMPIO → IIG → DVL → VALIDACIÓN DE LOTE → ID_RESOLUTION → INGESTIÓN
```

Y cumple estrictamente:

✔ validación estructural
✔ validación semántica
✔ validación global
✔ persistencia controlada

---

# 3. HALLAZGO CLAVE

Se confirma la existencia de:

## A. Campos sin cobertura en fuente

✔ comportamiento esperado
✔ no deben ser modificados

## B. Campos derivables no calculados

Ejemplo:

* max_power_kw ← power_cv
* top_speed_mph ← top_speed_kmh
* power_to_weight_*

## C. Campos parcialmente enriquecidos

✔ ya implementados en ESL v1
✔ demuestran viabilidad del modelo

---

# 4. DECISIÓN

Se aprueba la implementación de:

## 👉 ESL v2 — Enriquecimiento Semántico Determinista

---

# 5. POSICIÓN EN EL PIPELINE (OBLIGATORIA)

Se establece como flujo oficial:

```text
SCRAPER
→ DICT LIMPIO
→ IIG
→ DVL
→ VALIDACIÓN DE LOTE
→ ENRICHMENT (ESL v1 + v2)
→ ID_RESOLUTION
→ INGESTIÓN
```

❗ El enriquecimiento NO puede ejecutarse antes de VALIDACIÓN DE LOTE

---

# 6. PRINCIPIOS DE DISEÑO

Todas las reglas ESL v2 deberán cumplir:

✔ determinismo absoluto
✔ no sobrescribir datos de fuente
✔ ejecución condicional
✔ trazabilidad completa
✔ consistencia matemática

Se refuerza:

👉 “la validación define la verdad”
👉 “el enriquecimiento mejora la utilidad”

---

# 7. ALCANCE FUNCIONAL

---

## 7.1 Conversiones de potencia

```text
max_power_kw ← max_power_cv
specific_output_kw_l ← cálculo determinista
```

---

## 7.2 Conversiones de velocidad

```text
top_speed_mph ← top_speed_kmh
```

---

## 7.3 Métricas derivadas

```text
power_to_weight_cv_ton
power_to_weight_kw_ton
```

---

## 7.4 Conversión de consumo

```text
mpg_uk
mpg_us
```

---

# 8. NATURALEZA DE LOS DATOS GENERADOS

Se establece:

👉 los campos enriquecidos NO forman parte de la verdad base

Son:

👉 capa derivada del sistema

---

# 9. IMPACTO EN EL SISTEMA

---

## 9.1 Mejora de completitud

Incremento estimado:

```text
~3% → ~15–25%
```

---

## 9.2 Mejora analítica

Permite:

* comparativas reales
* rankings técnicos
* filtros avanzados
* métricas derivadas

---

## 9.3 Preparación para futuro

Impacto directo en:

* inferencia de versiones
* matching con T_Anuncios
* modelos de pricing
* machine learning

---

# 10. RIESGOS Y MITIGACIÓN

---

## Riesgo: inconsistencia

✔ mitigado con fórmulas estándar

## Riesgo: sobreescritura

✔ prohibida por diseño

## Riesgo: complejidad

✔ mitigado con arquitectura modular

---

# 11. ALINEACIÓN CON EL SISTEMA

Esta capa:

✔ respeta no inferencia
✔ respeta trazabilidad
✔ respeta separación de responsabilidades
✔ no altera identidad semántica

---

# 12. CAMBIO DE NIVEL DEL SISTEMA

Se establece oficialmente:

👉 Orbis Drive pasa de sistema de validación

a:

👉 sistema de generación de inteligencia sobre datos validados

---

# 13. ESTADO FINAL

VALIDACIÓN: CONSOLIDADA
INGESTIÓN: OPERATIVA
ENRIQUECIMIENTO: ACTIVADO

---

# 14. MENSAJE FINAL

“El sistema ya sabe qué es verdad…

ahora empieza a medir, comparar y entender esa verdad.”

---

# RESOLUCIÓN FINAL

✅ ESL v2 APROBADO
✅ ENRIQUECIMIENTO DETERMINISTA AUTORIZADO
🚀 ORBIS DRIVE EVOLUCIONA HACIA SISTEMA ANALÍTICO

---

**Dirección General**
Proyecto Orbis Drive
