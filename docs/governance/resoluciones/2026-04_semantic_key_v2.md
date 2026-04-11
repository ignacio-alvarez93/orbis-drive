# RESOLUCIÓN DE DIRECCIÓN GENERAL

## Refinamiento de la identidad semántica de versión — semantic_key_v2

**Proyecto:** Orbis Drive
**Fecha:** Abril 2026
**Estado:** 🚀 APROBADO — AJUSTE ESTRUCTURAL DEL MODELO SEMÁNTICO

---

# 1. RESUMEN EJECUTIVO

Se aprueba la implementación de una nueva definición de identidad semántica de versión:

👉 `semantic_key_v2`

con el objetivo de mejorar la representación de variantes reales dentro del catálogo técnico.

---

# 2. PROBLEMA IDENTIFICADO

Se ha detectado que la definición anterior:

```text
manufacturer + model + generation + version_name
```

provoca:

* colapso de variantes reales
* falsos duplicados
* pérdida de granularidad semántica

Especialmente en modelos con evolución interna:

👉 SEAT León

---

# 3. DECISIÓN

Se aprueba la redefinición de la clave semántica incorporando dimensión temporal.

---

# 4. NUEVA DEFINICIÓN OFICIAL

```text
manufacturer
+ model
+ generation
+ version_name
+ production_start_year
+ production_end_year
```

---

# 5. PRINCIPIOS PRESERVADOS

La nueva definición:

✔ no introduce inferencia
✔ no modifica datos
✔ no altera jerarquía
✔ utiliza únicamente información explícita

Cumple con:

👉 T_Versiones = tabla de verdad semántica

---

# 6. IMPACTO EN EL SISTEMA

Se espera:

* reducción de falsos duplicados
* incremento de versiones únicas
* mejor fidelidad al mercado real

Ejemplo validado:

```text
SEAT León
Antes: 136 versiones
Después: ~155–165 versiones
```

---

# 7. ALCANCE DEL CAMBIO

El ajuste afecta exclusivamente a:

```text
src/catalogo/validacion_lote/rules/
```

Concretamente:

* duplicates.py
* conflicts.py

---

# 8. COMPATIBILIDAD

Se confirma:

✔ scraper no afectado
✔ IIG no afectado
✔ DVL no afectado
✔ base de datos no modificada

---

# 9. RIESGOS CONTROLADOS

Riesgos:

* ausencia de años en algunas versiones
* incremento de cardinalidad

Mitigación:

✔ uso condicional de campos
✔ fallback controlado
✔ validación de lote estricta

---

# 10. CAMBIO DE NIVEL DEL SISTEMA

Se establece que el sistema ha alcanzado un nuevo nivel:

👉 de validación correcta
👉 a modelado preciso de la realidad

---

# 11. CONCLUSIÓN

Se declara:

👉 `semantic_key_v2` como estándar del sistema

👉 modelo preparado para datasets complejos

👉 sistema capaz de evolucionar sin degradar la verdad

---

# 12. MENSAJE FINAL

“El problema no era el dato…

era cómo lo estábamos identificando.”

---

# RESOLUCIÓN FINAL

✅ semantic_key_v2 APROBADO
✅ IDENTIDAD SEMÁNTICA REFINADA
🚀 SISTEMA PREPARADO PARA ESCALAR

**Dirección General**
Proyecto Orbis Drive
