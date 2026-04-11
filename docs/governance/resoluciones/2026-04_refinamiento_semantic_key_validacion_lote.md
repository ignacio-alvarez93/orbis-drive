# RESOLUCIÓN DE DIRECCIÓN GENERAL

## Refinamiento de la clave semántica de versión en VALIDACIÓN DE LOTE

**Proyecto:** Orbis Drive
**Fecha:** Abril 2026
**Estado:** 🚀 APROBADO — AJUSTE ARQUITECTÓNICO DE IDENTIDAD SEMÁNTICA

---

## 1. RESUMEN EJECUTIVO

Durante la ejecución de la VALIDACIÓN DE LOTE sobre dataset real del catálogo se ha detectado una limitación en la definición actual de identidad semántica de versión.

La clave vigente:

```text
manufacturer + model + generation + version_name
```

resulta insuficiente para distinguir correctamente variantes reales que comparten nombre comercial dentro de una misma generación.

---

## 2. DIAGNÓSTICO

Se establece que:

* no es un fallo de VALIDACIÓN DE LOTE
* no es un fallo de DVL
* no es un fallo del modelo de generaciones

La causa raíz es:

👉 **infra-definición de la identidad semántica de versión**

---

## 3. EFECTO EN EL SISTEMA

La clave actual provoca:

* falsos conflictos críticos
* falsos duplicados
* bloqueo de datasets potencialmente válidos

Esto afecta especialmente a:

* vehículos antiguos
* variantes con evoluciones internas
* ajustes de potencia o transmisión sin cambio de nombre comercial

---

## 4. DECISIÓN

Se aprueba refinar la definición de `semantic_key` en la capa de VALIDACIÓN DE LOTE.

---

## 5. NUEVA DEFINICIÓN MÍNIMA APROBADA

La nueva clave semántica base será:

```text
manufacturer
+ model
+ generation
+ version_name
+ production_start_year
+ production_end_year
```

---

## 6. DEFINICIÓN EXTENDIDA (CONDICIONAL)

Si tras la aplicación del ajuste persisten conflictos relevantes, se autoriza ampliar la clave a:

```text
manufacturer
+ model
+ generation
+ version_name
+ production_start_year
+ production_end_year
+ power_cv
+ fuel_type
```

Esta ampliación solo se aplicará si la redefinición mínima no resulta suficiente.

---

## 7. ALCANCE DEL CAMBIO

El ajuste impacta exclusivamente en:

```text
src/catalogo/validacion_lote/rules/duplicates.py
src/catalogo/validacion_lote/rules/conflicts.py
```

Concretamente:

👉 en la función de construcción de `semantic_key`

---

## 8. RESTRICCIONES

Queda expresamente prohibido:

* modificar `T_Generaciones`
* eliminar conflictos manualmente
* seleccionar valores arbitrarios
* introducir heurísticas de “mejor valor”
* relajar la validación semántica

---

## 9. PRINCIPIOS PRESERVADOS

La solución aprobada:

✔ no introduce inferencia
✔ no modifica el dato
✔ no altera la jerarquía
✔ no degrada `T_Versiones`

Y preserva el principio del sistema:

👉 `T_Versiones` es tabla de verdad semántica

---

## 10. RESULTADO ESPERADO

Tras aplicar este ajuste se espera:

* reducción significativa de falsos conflictos
* duplicados mejor definidos
* mayor fidelidad a la realidad técnica del vehículo
* mayor capacidad de validación del dataset

---

## 11. ACCIÓN AUTORIZADA

Se autoriza a Dirección de Infraestructura GitHub a:

1. actualizar `semantic_key` en VALIDACIÓN DE LOTE
2. versionar el cambio como ajuste arquitectónico
3. reejecutar la validación sobre dataset real
4. informar del resultado comparativo antes/después

---

## 12. MENSAJE FINAL

“El sistema no está fallando.

Está revelando que la identidad de una versión era más compleja de lo que habíamos modelado.”

---

## RESOLUCIÓN FINAL

✅ AJUSTE ARQUITECTÓNICO APROBADO
✅ REFINAMIENTO DE IDENTIDAD SEMÁNTICA AUTORIZADO
🚀 SISTEMA LISTO PARA EVOLUCIONAR SIN RELAJAR SU VERDAD

Dirección General
Proyecto Orbis Drive
