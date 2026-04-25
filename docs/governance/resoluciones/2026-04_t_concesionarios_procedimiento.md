1) RESOLUCIÓN OFICIAL DEL PROCEDIMIENTO
RESOLUCIÓN DE DIRECCIÓN DE ARQUITECTURA Y DESARROLLO
Procedimiento oficial del sistema T_Concesionarios

Proyecto: Orbis Drive
Fecha: Abril 2026
Estado: 🚀 APROBADO — MARCO OPERATIVO DEL PILAR COMERCIAL

1. Resumen ejecutivo

Se aprueba el procedimiento oficial de construcción del sistema:

👉 T_Concesionarios

como pilar estructural de Orbis Drive destinado a modelar actores profesionales del mercado automovilístico, en coherencia con la fase de pilares ya autorizada para el proyecto. T_Concesionarios ya estaba previsto como uno de esos pilares junto a T_Localizacion y T_Fuentes_Scraping.

El sistema deberá operar sobre dos fuentes principales de directorio profesional:

https://www.autocasion.com/profesional
https://www.coches.net/concesionarios/

Estas dos fuentes presentan cobertura nacional y estructura apta para extracción segmentada por territorio y/o fichas de establecimiento. Coches.net publica un directorio nacional por provincias, ciudades y marcas; Autocasión expone públicamente un directorio profesional y páginas territoriales/paginadas en resultados indexados.

2. Principio fundamental

Se establece como norma del sistema:

👉 el concesionario no entra por confianza; entra por verificación formal, trazabilidad y resolución territorial

Esto alinea T_Concesionarios con el manifiesto fundacional del proyecto, que fija separación de responsabilidades, no inferencia, trazabilidad completa y robustez sobre velocidad.

3. Naturaleza del sistema

Se establece oficialmente que:

T_Concesionarios no es una tabla auxiliar
T_Concesionarios no modela anuncios
T_Concesionarios modela actores comerciales profesionales identificables
la unidad operativa del sistema será la sede comercial identificable, no solo la empresa abstracta

El sistema debe responder:

quién vende, dónde vende y cómo queda identificado dentro del sistema

4. Fuentes oficiales aprobadas
4.1 Fuente A — Autocasión Profesional

Fuente pública de directorio profesional. En resultados indexados se observan:

directorio profesional nacional
páginas territoriales por provincia
fichas de concesionario
paginación pública
snippets con cifras altas de cobertura, como 3814 concesionarios en España y 662 en Madrid en resultados públicos indexados.
4.2 Fuente B — Coches.net Concesionarios

Fuente pública de directorio nacional. La página pública muestra:

navegación por provincias
navegación por ciudades grandes
navegación por marcas
mensajes de cobertura nacional
cifras como “Madrid más de 1500 concesionarios”, “Barcelona más de 1000”, “Valencia más de 500” y “Sevilla más de 500”.
5. Modelo organizativo de ejecución

Se aprueba el siguiente modelo de trabajo:

un subordinado responsable de Autocasión
un subordinado responsable de Coches.net
una coordinación central única, bajo Dirección de Arquitectura y Desarrollo del sistema T_Concesionarios

Ambos subordinados trabajarán sobre fuentes distintas, pero deberán producir:

mismo contrato de datos
mismo dict limpio exploratorio
mismo pipeline
mismo esquema de salida
mismas reglas de clasificación
misma política de pendientes y rechazados

La coordinación central será responsable de:

unificación metodológica
control de calidad cruzado
homologación de campos
comparación interfuente
deduplicación semántica posterior
consolidación del resultado final del sistema
6. Motor oficial de scraping

Se aprueba como motor oficial de scraping para esta fase:

👉 SeleniumBase

y se autoriza específicamente el uso de:

👉 Pure CDP Mode con sb_cdp.Chrome(...)

La documentación oficial de SeleniumBase indica que Pure CDP Mode no usa WebDriver para las acciones del navegador, se inicializa con from seleniumbase import sb_cdp y sb = sb_cdp.Chrome(url=None, **kwargs), y ejecuta las acciones directamente desde sb.

También queda reconocido que la API oficial incluye capacidades como:

activate_cdp_mode()
disconnect()
connect()
reconnect()
uc_open_with_reconnect()
Restricción operativa

Estas capacidades quedan autorizadas como herramientas de estabilidad técnica, compatibilidad de navegación y resiliencia del flujo

7. Fase obligatoria previa — scraping exploratorio

Antes de cerrar el esquema definitivo y antes de cualquier ingestión real, se aprueba como obligatoria la fase:

SCRAPING EXPLORATORIO
→ DICT EXPLORATORIO
→ ANÁLISIS DE COBERTURA Y CALIDAD
→ DISEÑO FINAL DE ESQUEMA

Cada subordinado deberá producir:

muestra exploratoria suficiente
mapa real de campos visibles
patrones de nombres
patrones de direcciones
patrones de contacto
presencia de redes sociales estables
estructura de paginación
estructura de fichas
trazabilidad por URL y timestamp
8. Flujo oficial aprobado

Se establece como flujo oficial de T_Concesionarios:

SCRAPER
→ STAGING
→ IIG_Concesionarios
→ NORMALIZACION_Concesionarios
→ DVL_Concesionarios
→ VALIDACION_LOTE_Concesionarios
→ ENRICHMENT_Concesionarios
→ ID_RESOLUTION_Concesionarios
→ INGESTION
→ REPORTE

Este flujo sigue el patrón ya consolidado por el sistema catálogo y por el pilar territorial. El pilar territorial dejó aprobado el pipeline formal con validación, normalización, resolución de identidad e ingestión controlada, y T_Concesionarios debe reutilizar esa disciplina sin duplicar la lógica territorial.

9. Integración obligatoria con T_Localizacion

Se establece como norma crítica:

👉 ningún concesionario será ingestable sin resolución territorial mínima suficiente contra T_Localizacion

Proceso obligatorio:

ubicacion_raw
→ normalización territorial
→ matching con T_Paises / T_Subdivisiones_Administrativas / T_Localidades
→ resolución persistible

Si el registro no puede resolverse territorialmente con base suficiente:

❌ no se ingesta
👉 pasa a pendiente_recuperable

Esto reutiliza el principio ya aprobado en T_Localizacion: la validación del dato y la persistencia del dato son responsabilidades separadas, y la identidad territorial persistible debe resolverse antes de insertar.

10. Identidad semántica oficial

Se aprueba como principio de identidad lógica de concesionario:

no usar autoincremental como identidad lógica
usar una semantic_key_concesionario determinística y trazable

Definición mínima aprobada:

nombre_canonical
+ localidad_id
+ direccion_texto_normalizada (si existe)

Fallback controlado:

nombre_canonical
+ localidad_id
+ codigo_postal
+ website_domain

concesionario_id se generará a partir de esa clave semántica estable.

11. Delimitación con Orbis-Presence

Se establece formalmente:

T_Concesionarios

Modela:

👉 identidad del actor comercial

Orbis-Presence

Modelará en el futuro:

👉 actividad, visibilidad, reputación y métricas dinámicas

Por tanto:

✔ se permiten referencias estables:

instagram_handle
instagram_profile_url
facebook_page_url
tiktok_handle
youtube_channel_url
google_business_profile_url
linkedin_page_url

❌ no se permiten métricas dinámicas:

followers
engagement
reputational scores
activity score
trends
12. Reglas de comportamiento del scraper

Se aprueban como normas operativas obligatorias:

navegación segmentada por territorio / paginación / ficha
extracción pausada y trazable
control de reintentos
logging estructurado
snapshots de HTML cuando haya fallos
separación entre descubrimiento de URLs y extracción de detalle
idempotencia de ejecución
almacenamiento de resultados crudos por fuente

Y se prohíbe:

scraping ciego sin observabilidad
hardcodear selectores sin capa de adaptación
mezclar scraping con validación semántica
ingestión directa desde el scraper
13. Clasificación oficial de resultados

Se establece el mismo modelo oficial del sistema:

INGESTABLE

Registro válido, identificado y territorialmente resoluble

PENDIENTE_RECUPERABLE

Registro potencialmente válido, pero aún no persistible

RECHAZADO_TECNICO

Registro roto, inconsistente o sin entidad comercial real

14. Entregables obligatorios

Se aprueba como entregable mínimo del procedimiento:

scraping exploratorio real por fuente
dict exploratorio por fuente
análisis comparado de campos
contrato único homologado
esquema SQL final
pipeline funcional
dataset de prueba
reporte JSON
documentación técnica
consolidación interfuente coordinada
15. Mensaje final

“El sistema de concesionarios no se limita a recoger nombres.
Debe identificar actores reales del mercado, ubicarlos con rigor y convertirlos en entidades persistibles del sistema.”