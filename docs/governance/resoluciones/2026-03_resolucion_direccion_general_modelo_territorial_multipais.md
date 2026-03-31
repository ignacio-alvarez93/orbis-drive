📄 RESOLUCIÓN DE DIRECCIÓN GENERAL
Rediseño del modelo territorial — Arquitectura multipaís

Proyecto: Orbis Drive
Área emisora: Dirección General
Destinatarios: Dirección de Base de Datos / Dirección de Scraping / Dirección de QA / Dirección de Datos
Fecha: Marzo 2026
Estado: 🚀 APROBADO — MODELO TERRITORIAL MULTIPAÍS

1. RESUMEN EJECUTIVO

Tras la revisión del modelo territorial actual basado en:

T_Paises → T_Provincias → T_Municipios

Dirección General determina que:

⚠️ dicho modelo no es válido como arquitectura global del sistema

Motivo:

👉 Orbis Drive es una plataforma multipaís (España-UE y expansión futura)
👉 Las estructuras administrativas varían entre países
👉 El modelo actual está sesgado hacia España

Esto entra en conflicto con el principio fundacional del sistema:

“Si una decisión rompe la coherencia del sistema, es incorrecta”

2. DECISIÓN ESTRATÉGICA

Se aprueba el rediseño del modelo territorial hacia un sistema:

👉 AGNÓSTICO AL PAÍS
👉 ESCALABLE
👉 NORMALIZABLE SEMÁNTICAMENTE
3. NUEVO MODELO TERRITORIAL APROBADO

Se define la siguiente estructura:

T_Paises
↓
T_Subdivisiones_Administrativas
↓
T_Localidades
4. DEFINICIÓN DE LAS TABLAS
4.1 T_Paises

Tabla de verdad de países.

Campos base:
id
nombre
codigo_iso
region_global (opcional)
4.2 T_Subdivisiones_Administrativas

Tabla genérica para niveles administrativos intermedios.

Objetivo

Modelar cualquier tipo de división territorial:

comunidad autónoma
provincia
estado
región
departamento
cantón
condado
Campos base:
id
nombre
tipo_subdivision (ENUM o tabla auxiliar)
nivel (entero jerárquico)
pais_id
parent_id (nullable, para jerarquía)
Ejemplo conceptual

España:

nivel 1 → comunidad autónoma
nivel 2 → provincia

Alemania:

nivel 1 → Land

Francia:

nivel 1 → región
nivel 2 → departamento
4.3 T_Localidades

Tabla de ciudades / municipios / localidades.

Campos base:
id
nombre
subdivision_id
pais_id
tipo_localidad (opcional)
5. PRINCIPIO FUNDAMENTAL

Se establece como norma oficial:

El modelo territorial de Orbis Drive no depende de la estructura administrativa de un país concreto
6. COMPATIBILIDAD CON ESPAÑA

Se confirma:

✅ España se mantiene como primer caso de implementación

Ejemplo:

España
→ Comunidad Autónoma (nivel 1)
→ Provincia (nivel 2)
→ Municipio (localidad)

Sin alterar el modelo general.

7. IMPACTO EN EL SISTEMA
7.1 Base de datos
eliminación progresiva de:
T_Provincias
T_Municipios
sustitución por:
T_Subdivisiones_Administrativas
T_Localidades
7.2 DVL territorial

Debe adaptarse para:

resolver jerarquías dinámicas
mapear input a subdivisiones correctas
no depender de nombres fijos como “provincia”
7.3 Contratos de datos

El dict de entrada debe permitir:

ubicación_raw
localidad
subdivisión
país
7.4 Scraping

No debe asumir:

estructuras fijas
nombres administrativos concretos
8. PRINCIPIO DE DISEÑO

Se refuerza:

Catálogo ≠ Mercado

Y se añade:

Territorio ≠ España
9. RIESGOS ELIMINADOS

Este rediseño elimina:

dependencia estructural de España
necesidad de rehacer el modelo al entrar en otro país
incoherencias territoriales multipaís
duplicidad de lógica por país
10. MOMENTO DE LA DECISIÓN

Dirección General establece que:

👉 este cambio se realiza AHORA
👉 antes de ingestión masiva
👉 antes de escalar el sistema
11. ESTADO FINAL
MODELO TERRITORIAL MULTIPAÍS: APROBADO
MODELO ANTERIOR: DEPRECADO
SISTEMA: PREPARADO PARA ESCALAR GLOBALMENTE
12. RESOLUCIÓN FINAL
✅ REDISEÑO TERRITORIAL APROBADO
✅ MODELO MULTIPAÍS OFICIAL
🚀 IMPLEMENTACIÓN AUTORIZADA
🧠 MENSAJE FINAL DE DIRECCIÓN GENERAL

“Orbis Drive no modela España…
modela el mundo.”

Dirección General
Proyecto Orbis Drive 🚀