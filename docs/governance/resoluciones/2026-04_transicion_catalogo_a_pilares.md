# RESOLUCIÓN DE DIRECCIÓN GENERAL

## Transición estratégica del sistema catálogo a pilares estructurales del sistema

**Proyecto:** Orbis Drive
**Fecha:** Abril 2026
**Estado:** 🚀 APROBADO — FASE INTERMEDIA DEL SISTEMA

---

# 1. RESUMEN EJECUTIVO

Tras la consolidación completa del sistema catálogo, se aprueba la transición hacia una nueva fase estructural del proyecto:

👉 construcción de los pilares fundamentales del sistema

Esta fase precede obligatoriamente a la activación del sistema de mercado.

---

# 2. ESTADO ACTUAL DEL SISTEMA

Se confirma:

✔ T_Versiones completamente operativa
✔ ingestión completa de SEAT Ibiza y SEAT León
✔ identidad semántica consolidada (`semantic_key_v2`)
✔ pipeline validado end-to-end
✔ enriquecimiento semántico activo (ESL v2)

Se establece:

👉 T_Versiones = sistema estable (V1)

---

# 3. PRINCIPIO ESTRATÉGICO

Se introduce el siguiente principio:

👉 el sistema de mercado no puede construirse sin pilares estructurales previos

Esto refuerza el manifiesto del proyecto:

👉 robustez sobre velocidad
👉 separación de responsabilidades

---

# 4. DECISIÓN ESTRATÉGICA

Se establece el siguiente flujo de evolución del sistema:

```text
CATÁLOGO → PILARES → MERCADO
```

---

# 5. FASE ACTUAL AUTORIZADA

## 🟡 CONSTRUCCIÓN DE PILARES DEL SISTEMA

Se aprueba el desarrollo de las siguientes entidades:

---

## 5.1 T_Localización

Basada en modelo multipaís aprobado:

```text
T_Paises
→ T_Subdivisiones_Administrativas
→ T_Localidades
```

Objetivo:

✔ normalización territorial global
✔ base geográfica del sistema
✔ soporte para mercado

---

## 5.2 T_Concesionarios

Objetivo:

✔ modelar actores reales del mercado
✔ identificar vendedores profesionales
✔ diferenciar particular vs concesionario
✔ base para análisis B2B

Campos esperados:

* nombre
* ubicación
* tipo (concesionario, compraventa, etc.)
* identificadores externos
* relación con anuncios (futuro)

---

## 5.3 T_Fuentes_Scraping

Objetivo:

✔ trazabilidad completa del origen del dato
✔ control de calidad por fuente
✔ auditoría del sistema de scraping
✔ soporte para sistema multi-fuente

Campos esperados:

* nombre fuente
* tipo (web, API, manual)
* país
* fiabilidad
* fecha de extracción

---

# 6. PRINCIPIO ARQUITECTÓNICO CONSOLIDADO

Se refuerza:

```text
Catálogo ≠ Mercado
Pilares ≠ Catálogo
Pilares ≠ Mercado
```

Cada bloque cumple una función independiente.

---

# 7. POSICIÓN EN EL SISTEMA

La arquitectura evoluciona a:

```text
SCRAPER
→ CATÁLOGO (T_Versiones)
→ PILARES (Localización, Concesionarios, Fuentes)
→ MERCADO (T_Anuncios)
→ ANALÍTICA
```

---

# 8. RESTRICCIÓN CRÍTICA

Se establece:

⛔ T_Anuncios NO puede iniciarse hasta que los pilares estén operativos

Motivo:

👉 evitar incoherencias estructurales
👉 garantizar calidad de datos de mercado
👉 asegurar trazabilidad completa

---

# 9. IMPACTO EN EL SISTEMA

Este enfoque permite:

✔ sistema modular y escalable
✔ integración multi-fuente controlada
✔ base sólida para mercado
✔ eliminación de dependencias implícitas

---

# 10. CAMBIO DE NIVEL

Se establece oficialmente:

👉 Orbis Drive evoluciona de sistema de catálogo

a:

👉 sistema estructural completo preparado para mercado

---

# 11. SIGUIENTE FASE (CONDICIONAL)

Una vez completados los pilares:

## 🚀 se autoriza iniciar T_Anuncios

Objetivo:

✔ captura de mercado real
✔ análisis de precios
✔ comportamiento de oferta

---

# 12. MENSAJE FINAL

“No se puede analizar el mercado…

sin entender antes quién vende, dónde vende y desde qué fuente.”

---

# RESOLUCIÓN FINAL

✅ T_VERSIONES DECLARADA ESTABLE
✅ FASE DE PILARES AUTORIZADA
⛔ T_ANUNCIOS BLOQUEADO TEMPORALMENTE
🚀 SISTEMA PREPARADO PARA CONSTRUCCIÓN ESTRUCTURAL

---

**Dirección General**
Proyecto Orbis Drive
