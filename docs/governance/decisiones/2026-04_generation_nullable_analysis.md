# INFORME A DIRECCIÓN GENERAL

## Evaluación de adaptación futura del modelo T_Versiones para admitir generation_id NULL

**Proyecto:** Orbis Drive
**Fecha:** Abril 2026
**Estado:** 📊 ANÁLISIS COMPLETADO — DECISIÓN DIFERIDA

---

## 1. CONTEXTO

Durante la fase de preparación de ingestión de `T_Versiones` se ha detectado que una parte no despreciable de los vehículos:

* no dispone de generación identificable
* o no incluye esta información en la fuente de datos

El modelo actual exige:

👉 `generation_id` obligatorio en `T_Versiones`

---

## 2. SITUACIÓN ACTUAL

El sistema actual:

* bloquea correctamente registros sin generación
* evita persistencia de identidad incompleta
* mantiene integridad jerárquica estricta

Sin embargo:

👉 limita la cobertura del catálogo

---

## 3. EVALUACIÓN

Se concluye que:

* la obligatoriedad de generación es adecuada para modelos modernos y bien estructurados
* pero excluye una parte real del mercado

Esto genera una tensión entre:

* calidad semántica
* cobertura de datos

---

## 4. OPCIÓN DE ADAPTACIÓN

Se evalúa la posibilidad de permitir:

👉 `generation_id = NULL`

en `T_Versiones`

---

## 5. IMPLICACIONES

### 5.1 A nivel de base de datos

* modificación del schema
* revisión de claves únicas
* adaptación de integridad referencial

### 5.2 A nivel de sistema

* adaptación de `ID_RESOLUTION`
* adaptación de ingestión
* redefinición de reglas de duplicado
* actualización del contrato de datos

---

## 6. RIESGOS

El principal riesgo es:

👉 pérdida de capacidad de diferenciación entre versiones

Especialmente en modelos con múltiples generaciones no identificadas correctamente.

---

## 7. DECISIÓN ACTUAL

Se establece:

👉 **NO modificar el modelo en esta fase**

---

## 8. CRITERIO OPERATIVO

La ingestión inicial se limitará a:

👉 vehículos con generación resoluble

Esto permite:

* validar el sistema en condiciones controladas
* operar con el caso dominante del mercado
* evitar rediseños prematuros

---

## 9. PLAN FUTURO

Se establece como línea de evolución:

* medir volumen real de casos sin generación
* evaluar impacto en cobertura
* diseñar rediseño controlado si procede

---

## 10. CONCLUSIÓN

El sistema mantiene su modelo actual en fase inicial, priorizando:

✔ robustez
✔ coherencia
✔ integridad semántica

sin descartar una evolución futura basada en evidencia.

---

**Dirección General**
Proyecto Orbis Drive
