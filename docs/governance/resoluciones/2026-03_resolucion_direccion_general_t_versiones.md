📄 2. RESOLUCIÓN DE DIRECCIÓN GENERAL
(DOCUMENTO OFICIAL — PARA GITHUB / FUENTE DEL PROYECTO)
📄 RESOLUCIÓN DE DIRECCIÓN GENERAL
Marco definitivo de ingestión de T_Versiones

Proyecto: Orbis Drive
Fecha: Marzo 2026
Estado: 🚀 APROBADO — MARCO FUNDACIONAL DEL SISTEMA

1. RESUMEN EJECUTIVO

Tras la validación conjunta de:

Dirección de Base de Datos
Dirección de Scraping

Dirección General establece el marco definitivo y obligatorio para la ingestión de:

👉 T_Versiones
2. NATURALEZA DE T_VERSIONES

Se establece de forma explícita:

T_Versiones = TABLA DE VERDAD SEMÁNTICA DEL VEHÍCULO
Implicaciones
no es una tabla operativa
no es corregible sin impacto sistémico
no admite degradación progresiva
es base de:
validación de anuncios
tasador
analítica avanzada
3. FLUJO OFICIAL APROBADO
SCRAPER
↓
DICT LIMPIO (CONTRATO 1:1 DB)
↓
IIG (CONTROL ESTRUCTURAL)
↓
DVL (VALIDACIÓN SEMÁNTICA)
↓
VALIDACIÓN DE LOTE
↓
INGESTIÓN
4. PRINCIPIO FUNDAMENTAL
T_Versiones no se carga por confianza
T_Versiones se carga por verificación formal
5. DEFINICIÓN DE IIG PARA T_VERSIONES
Estado: OBLIGATORIO — MODO ESTRICTO
Función

👉 Guardián del contrato de datos

Debe:
validar esquema exacto
validar claves obligatorias
validar tipos
rechazar desviaciones
No puede:
modificar datos
inferir valores
6. DEFINICIÓN DE DVL PARA T_VERSIONES
Estado: OBLIGATORIA — MODO CONSERVADOR
Función

👉 cierre semántico del dato

Permitido:
canonicalización controlada
normalización de enums
validación de coherencia técnica
Prohibido:
inferencias
reconstrucción de datos
heurísticas agresivas
7. VALIDACIÓN DE LOTE
Estado: OBLIGATORIA

Debe garantizar:

unicidad semántica
coherencia por generación
ausencia de duplicados
cobertura estructural
8. SEPARACIÓN ARQUITECTÓNICA OBLIGATORIA

Se establece como norma del sistema:

❗ T_Versiones y T_Anuncios NO comparten pipeline
Se crean dos sistemas independientes:
Sistema CATÁLOGO
IIG_Catalogo
DVL_Catalogo

👉 aplicable a T_Versiones

Sistema MERCADO
IIG_Mercado
DVL_Mercado

👉 aplicable a T_Anuncios

9. PRINCIPIO DE DISEÑO
Catálogo ≠ Mercado
10. CONDICIONES DE INGESTIÓN

Se autoriza la ingestión de T_Versiones solo si:

dict_limpio alineado con DB
IIG superado
DVL superado
validación de lote superada
11. IMPACTO EN EL SISTEMA

Este marco garantiza:

eliminación de errores estructurales
catálogo estable
base fiable para todo el sistema
escalabilidad futura
12. ALINEACIÓN CON ORBIS DRIVE

Este modelo cumple:

👉 ROBUSTEZ SOBRE VELOCIDAD
👉 SEPARACIÓN DE RESPONSABILIDADES
👉 CONTROL TOTAL DEL DATO
13. ESTADO FINAL
T_VERSIONES: LISTA PARA INGESTIÓN CONTROLADA
ARQUITECTURA: CONSOLIDADA
SISTEMA: PREPARADO PARA ESCALAR
🧠 MENSAJE FINAL DE DIRECCIÓN GENERAL

“El mercado se puede limpiar después…
el catálogo debe ser correcto desde el primer día.”

🟢 RESOLUCIÓN FINAL
✅ FLUJO APROBADO
✅ ARQUITECTURA DEFINITIVA
🚀 INGESTIÓN AUTORIZADA BAJO CONTROL ESTRICTO

Dirección General
Proyecto Orbis Drive