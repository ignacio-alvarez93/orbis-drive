# RESOLUCIÓN DE DIRECCIÓN GENERAL

## Delimitación de responsabilidades DVL vs Enriquecimiento Semántico

**Proyecto:** Orbis Drive
**Fecha:** Abril 2026
**Estado:** 🚀 APROBADO — NUEVA CAPA ARQUITECTÓNICA DEL SISTEMA

---

# 1. RESUMEN EJECUTIVO

Tras la ingestión completa de:

* SEAT Ibiza
* SEAT León

y la auditoría de calidad sobre `T_Versiones`, se ha identificado una brecha estructural entre:

👉 dato válido (pipeline actual)
👉 dato analíticamente útil

Se aprueba la incorporación de una nueva capa:

👉 **SEMANTIC_ENRICHMENT_LAYER**

---

# 2. CONTEXTO DEL SISTEMA

El sistema actual ejecuta:

```text
SCRAPER → DICT LIMPIO → IIG → DVL → VALIDACIÓN DE LOTE → ID_RESOLUTION → INGESTIÓN
```

Y cumple estrictamente:

✔ validación estructural
✔ validación semántica
✔ validación global

---

# 3. HALLAZGO CLAVE

Se detecta la existencia de:

### A. Campos sin cobertura en fuente

✔ comportamiento correcto

### B. Campos presentes pero no persistidos

❗ pérdida de transformación semántica

### C. Campos derivados no calculados

❗ ausencia de capa de lógica posterior

---

# 4. PROBLEMA IDENTIFICADO

El sistema carece de una capa responsable de:

👉 transformar datos válidos en datos utilizables

Sin violar:

* no inferencia
* no modificación de verdad
* trazabilidad

---

# 5. DECISIÓN

Se aprueba la creación de:

## 👉 SEMANTIC_ENRICHMENT_LAYER

---

# 6. POSICIÓN EN EL PIPELINE

Se establece como flujo oficial:

```text
SCRAPER
→ DICT LIMPIO
→ IIG
→ DVL
→ VALIDACIÓN DE LOTE
→ ENRICHMENT
→ ID_RESOLUTION
→ INGESTIÓN
```

---

# 7. PRINCIPIO FUNDAMENTAL

Se establece:

👉 la validación define la verdad
👉 el enriquecimiento mejora la utilidad

Nunca al revés.

---

# 8. RESPONSABILIDADES DE LA CAPA

La capa de enriquecimiento:

✔ trabaja solo sobre datos validados
✔ no modifica campos originales
✔ genera campos derivados
✔ realiza normalización semántica controlada
✔ mantiene trazabilidad completa

---

# 9. PROHIBICIONES

Queda explícitamente prohibido:

❌ alterar valores originales
❌ introducir inferencia no determinista
❌ afectar a la identidad semántica
❌ interferir con validación de lote

---

# 10. CASOS DE USO APROBADOS

## Gearbox

```json
gearbox_label → gearbox_type
```

## Boot capacity

```json
boot_capacity_l → min/max
```

## Trim

```json
version_name → trim
```

## Estado de generación

```json
production_end_year → is_current_generation
```

---

# 11. NATURALEZA DE LOS DATOS GENERADOS

Se establece:

👉 los campos enriquecidos NO forman parte de la verdad base

Son:

👉 capa derivada del sistema

---

# 12. UBICACIÓN EN REPOSITORIO

```text
src/catalogo/enrichment/
```

Estructura recomendada:

```text
enrichment/
├── core/
├── rules/
├── mappers/
└── enrichment_engine.py
```

---

# 13. RELACIÓN CON OTRAS CAPAS

| Capa          | Rol           |
| ------------- | ------------- |
| IIG           | estructura    |
| DVL           | coherencia    |
| LOTE          | verdad global |
| ENRICHMENT    | utilidad      |
| ID_RESOLUTION | persistencia  |

---

# 14. IMPACTO EN EL SISTEMA

Este cambio permite:

✔ aumentar cobertura efectiva
✔ mejorar capacidad analítica
✔ preparar sistema para ML / pricing
✔ mantener integridad semántica

---

# 15. ALINEACIÓN CON PRINCIPIOS

Se refuerzan:

* separación de responsabilidades
* mejor NULL que dato incorrecto
* no inferencia
* trazabilidad completa

---

# 16. CAMBIO DE NIVEL DEL SISTEMA

Se establece oficialmente:

👉 Orbis Drive pasa de validar datos
a transformar datos en inteligencia

---

# 17. SIGUIENTE FASE AUTORIZADA

Se autoriza iniciar:

👉 desarrollo de `semantic_enrichment_layer`

---

# 18. MENSAJE FINAL

“El sistema ya sabe qué datos son verdad…

ahora empieza a convertir esa verdad en conocimiento.”

---

# RESOLUCIÓN FINAL

✅ CAPA DE ENRIQUECIMIENTO APROBADA
✅ ARQUITECTURA ACTUAL EXTENDIDA
🚀 ORBIS DRIVE EVOLUCIONA HACIA CAPA ANALÍTICA

---

**Dirección General**
Proyecto Orbis Drive
