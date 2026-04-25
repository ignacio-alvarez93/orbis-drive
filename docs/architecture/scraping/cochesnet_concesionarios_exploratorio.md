# 📄 INFORME A DIRECCIÓN — COCHES.NET (T_Concesionarios)

**Proyecto:** Orbis Drive  
**Área:** Dirección Técnica / Scraping & Data Acquisition  
**Fuente analizada:** https://www.coches.net/concesionarios  
**Fecha:** Abril 2026  
**Estado:** ✅ FASE EXPLORATORIA COMPLETADA

---

# 1. RESUMEN EJECUTIVO

Se ha completado la fase exploratoria de la fuente **Coches.net Concesionarios**, validando:

- Viabilidad técnica del scraping
- Estructura navegacional del portal
- Extracción de fichas individuales de concesionarios
- Generación de dataset exploratorio real

📊 Resultado:

- **59 concesionarios reales extraídos**
- Pipeline completo funcional (discovery → captura → parsing → raw)
- Modelo de datos consistente y reutilizable

👉 **Conclusión:**  
La fuente es **VIABLE y ESTRATÉGICA** para el sistema **T_Concesionarios**

---

# 2. ARQUITECTURA DEL PORTAL

## 2.1 Tipos de rutas detectadas

El portal presenta una estructura jerárquica clara:

### Nivel 1 — Entrada general

/concesionarios/


### Nivel 2 — Segmentación principal

- Por provincia:

/concesionarios/madrid/


- Por marca:

/concesionarios/seat/


---

### Nivel 3 — Combinaciones

- Marca + provincia:

/concesionarios/seat/madrid/


- Provincia + localidad:

/concesionarios/madrid/alcobendas/


---

### Nivel 4 — Ficha de concesionario


/concesionario/<slug>/


👉 Este nivel es el **objetivo principal del sistema**

---

# 3. PIPELINE IMPLEMENTADO

## 3.1 Discovery

- Extracción masiva de rutas desde HTML
- Clasificación en:
  - provincias
  - marcas
  - combinaciones
  - fichas

## 3.2 Captura

- Script:

cochesnet_fetch_and_clean.py


- Generación:
  - HTML bruto
  - HTML limpio
  - logs

## 3.3 Parsing

- Script:

cochesnet_parse_detail_html.py


- Filtro crítico:
```python
if "/concesionario/" not in canonical_url:
    continue

👉 Garantiza solo fichas reales

3.4 Generación RAW exploratorio
Script:
build_raw_exploratorio_cochesnet.py
Output:
raw_exploratorio_cochesnet.json
4. MODELO DE DATOS OBSERVADO

Cada concesionario contiene:

{
  "record_external_id": "string",
  "dealer_name_raw": "string",
  "address_raw": "string",
  "postal_code_raw": "string",
  "location_raw": "string",
  "source_row_url": "string"
}
4.1 Ejemplo real
{
  "record_external_id": "35motor",
  "dealer_name_raw": "35 Motor",
  "address_raw": "Calle Roma 9 28813 Torres de la Alameda Madrid",
  "postal_code_raw": "28813",
  "location_raw": "Torres de la Alameda Madrid",
  "source_row_url": "https://www.coches.net/concesionario/35motor/"
}
5. CALIDAD DE DATOS
5.1 Cobertura
Campo	Cobertura
record_external_id	✅ Alta
dealer_name_raw	✅ Alta
address_raw	✅ Alta
postal_code_raw	✅ Alta
location_raw	✅ Alta
5.2 Problemas detectados
⚠️ 1. Encoding (mojibake)

Ejemplos:

Veh▒culos
Garc▒a

👉 Causa:

Decodificación inconsistente (UTF-8 / latin-1)

👉 Impacto:

Requiere normalización en pipeline
⚠️ 2. Nombres incompletos

Ejemplo:

tucochellaveenmano | ...

👉 Causa:

fallback HTML no consistente
⚠️ 3. Direcciones no normalizadas

Ejemplos:

Valencia Valencia
Zaragoza Capital Zaragoza

👉 Impacto:

dependencia directa de T_Localización
6. INTEGRACIÓN CON ORBIS
6.1 T_Localización

✔ Totalmente compatible

Se requiere:

normalización de:
provincia
municipio
código postal
6.2 Orbis Presence (futuro)

Limitación actual:

❌ No se detectan:

redes sociales
email
teléfono

👉 Solución futura:

Scraping ficha Coches.net
Scraping web del concesionario
Scraping redes sociales
7. VIABILIDAD
Criterio	Estado
Acceso HTML	✅
Estructura estable	✅
Parsing fiable	✅
Datos útiles	✅
Escalabilidad	✅
8. DECISIÓN DE DIRECCIÓN

👉 Se aprueba:

✅ Uso de Coches.net como fuente oficial para T_Concesionarios
✅ Paso a fase de diseño de scraper productivo
✅ Integración futura con T_Localización

9. SIGUIENTES PASOS
9.1 Corto plazo
Construcción scraper definitivo
Normalización encoding
limpieza de nombres
9.2 Medio plazo
Integración con:
T_Localización
sistema de direcciones
9.3 Largo plazo
Enriquecimiento:
webs propias
redes sociales
presencia digital
10. CONCLUSIÓN FINAL

La fuente Coches.net Concesionarios:

👉 es estructuralmente sólida
👉 aporta datos de alto valor
👉 escala correctamente

📌 Se considera pilar fundamental del sistema T_Concesionarios

Estado final:
✅ EXPLORACIÓN COMPLETADA
🚀 LISTO PARA FASE DE PRODUCCIÓN