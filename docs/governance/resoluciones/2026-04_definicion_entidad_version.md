# RESOLUCIÓN DE DIRECCIÓN GENERAL

## Definición oficial de la entidad “Versión” en Orbis Drive

**Proyecto:** Orbis Drive
**Fecha:** Abril 2026
**Estado:** 🚀 APROBADO — DEFINICIÓN FUNDACIONAL DEL MODELO DE CATÁLOGO

---

# 1. OBJETIVO

Establecer una definición formal, única y operativa de la entidad:

👉 **Versión de vehículo**

como base estructural del sistema catálogo de Orbis Drive.

Esta definición tiene como finalidad:

* eliminar ambigüedades en ingestión y validación
* diferenciar correctamente variantes reales y conflictos
* garantizar coherencia semántica global
* permitir escalabilidad multipaís

---

# 2. DEFINICIÓN EJECUTIVA

> Una versión de vehículo es la unidad mínima comercializable definida por el fabricante dentro de un modelo (y, cuando exista, una generación), caracterizada por una combinación coherente de atributos técnicos y posicionamiento comercial en un intervalo temporal determinado.

---

# 3. DEFINICIÓN OPERATIVA

Una versión queda definida por la intersección de tres ejes:

---

## 3.1 Identidad base

* manufacturer
* model
* generation (cuando exista)
* version_name

👉 Representa la intención comercial del fabricante

---

## 3.2 Identidad técnica (coherencia, no completitud)

Una versión debe ser **técnicamente coherente**, pero no necesariamente completa.

Campos típicos:

* power_cv (si existe)
* fuel_type
* gearbox_type / drive_type (si existen)
* engine_displacement (si existe)

👉 Regla fundamental:

✔ los campos pueden ser NULL
✔ lo obligatorio es que **no exista contradicción interna**

---

## 3.3 Identidad temporal

* production_start_year
* production_end_year

👉 Permite diferenciar:

* evoluciones internas
* actualizaciones técnicas
* coexistencia de variantes

---

# 4. PRINCIPIOS FUNDAMENTALES

---

## 4.1 El nombre comercial no es único

`version_name` no identifica una versión de forma unívoca.

👉 Puede haber múltiples versiones con el mismo nombre.

---

## 4.2 Separación versión vs acabado

* Versión = definición técnica
* Acabado (trim) = equipamiento

👉 El acabado NO forma parte de la entidad versión

---

## 4.3 Dependencia temporal

Una misma configuración técnica:

* puede ser una única versión
* o varias versiones si ocurre en periodos distintos

---

## 4.4 No inferencia en catálogo

El sistema catálogo:

❌ no inventa versiones
❌ no corrige datos
❌ no completa información

✔ solo valida coherencia

---

# 5. CLASIFICACIÓN DE CASOS

---

## 5.1 Duplicado

Misma identidad semántica completa

👉 Acción:

* consolidar
* no bloquear ingestión

---

## 5.2 Variante válida

Misma base, pero:

* distinto periodo, o
* diferencia técnica coherente

👉 Acción:

* coexistencia permitida

---

## 5.3 Conflicto

Misma identidad base + mismo periodo + contradicción técnica

👉 Acción:

* error crítico
* bloqueo de ingestión

---

# 6. REPRESENTACIÓN EN EL SISTEMA

---

## 6.1 Clave semántica oficial

Se establece como estándar:

```text
manufacturer
+ model
+ generation
+ version_name
+ production_start_year
+ production_end_year
```

Fallback:

```text
+ power_cv
+ fuel_type
```

---

## 6.2 Aplicación en el sistema

Esta definición se aplica a:

* VALIDACIÓN DE LOTE
* ID_RESOLUTION
* INGESTIÓN
* BASE DE DATOS (`T_Versiones`)
* ORQUESTADOR

---

# 7. RELACIÓN CON EL MODELO GLOBAL

Esta definición:

✔ es compatible con `semantic_key_v2`
✔ se alinea con T_Versiones como tabla de verdad semántica
✔ respeta el pipeline oficial del sistema 

---

# 8. IMPLICACIONES ESTRATÉGICAS

Permite:

* ingestión masiva sin falsos conflictos
* representación fiel del mercado real
* base sólida para analítica y mercado
* escalabilidad a nuevos países y fabricantes

---

# 9. CONCLUSIÓN

La entidad “versión” no se define por su nombre, sino por:

* intención comercial
* coherencia técnica
* contexto temporal

👉 Esta definición se establece como:

## 🔵 ESTÁNDAR OFICIAL DEL SISTEMA ORBIS DRIVE

---

# 10. MENSAJE FINAL

“La verdad del catálogo no está en cómo se llama una versión…

sino en lo que realmente representa en el tiempo.”

---

# RESOLUCIÓN FINAL

✅ DEFINICIÓN DE “VERSIÓN” APROBADA
✅ MODELO SEMÁNTICO CONSOLIDADO
🚀 BASE FUNDACIONAL DEL CATÁLOGO ESTABLECIDA

---

**Dirección General**
Proyecto Orbis Drive
