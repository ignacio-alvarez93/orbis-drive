# Orbis Drive

Orbis Drive es una plataforma de inteligencia de mercado automovilístico con alcance España-UE y proyección multipaís.

Surge como evolución de Mercado Ibiza, heredando su arquitectura y principios, pero ampliando su alcance hacia un sistema multimarca y multipaís.

Su objetivo es transformar datos desestructurados en inteligencia de mercado útil para usuarios B2C y empresas B2B.

---

## Principio rector

> Si una decisión rompe la coherencia del sistema, es incorrecta.

Este principio gobierna tanto la arquitectura del dato como la estructura del repositorio.

---

## Arquitectura base del sistema

```text
SCRAPERS → DICT LIMPIO → IIG → DVL → PIPELINE → BASE DE DATOS → ANALÍTICA
Esta arquitectura no representa un conjunto de scripts independientes, sino un sistema estructurado de captura, validación, ingestión y explotación de datos.

Principios del sistema
Separación de responsabilidades
Mejor NULL que dato incorrecto
Trazabilidad completa
No inferencia sin base
Robustez sobre velocidad
Naturaleza del repositorio

El repositorio GitHub de Orbis Drive es la fuente única de verdad estructural del proyecto.

Esto implica que el repositorio debe reflejar de forma exacta:

la arquitectura del sistema
las responsabilidades por capa
los contratos de datos
la documentación oficial
la separación entre catálogo y mercado
la base para la evolución multipaís

El repositorio no es un contenedor de archivos.
Es la representación formal del sistema.

Separación estructural obligatoria

Orbis Drive distingue de forma estricta entre dos sistemas:

Sistema Catálogo

Responsable de la verdad semántica del vehículo.

Ubicación principal:

src/catalogo/

Capas previstas:

IIG_Catalogo
DVL_Catalogo
validación de lote
pipeline de ingestión de catálogo
Sistema Mercado

Responsable de la capa operativa de anuncios y mercado.

Ubicación principal:

src/mercado/

Capas previstas:

IIG_Mercado
DVL_Mercado
pipeline de ingestión de mercado
Regla de diseño
Catálogo ≠ Mercado

No comparten:

pipeline
validaciones
responsabilidades
semántica de dato
T_Versiones — tabla de verdad del vehículo

T_Versiones es la tabla de verdad semántica del vehículo dentro del sistema catálogo.

Naturaleza
no es una tabla operativa
no es corregible sin impacto sistémico
no admite degradación progresiva
es base de validación, tasación y analítica avanzada
Flujo oficial aprobado
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
Principio operativo

T_Versiones no se carga por confianza.

Se carga por verificación formal.

Contratos de datos

Los contratos de datos viven en:

contracts/catalogo/
contracts/mercado/

El contrato actual central del sistema catálogo es:

contracts/catalogo/t_versiones.contract.json

Este contrato define la estructura formal del dato y actúa como referencia única para:

IIG_Catalogo
DVL_Catalogo
pipeline de ingestión
validación estructural automatizable
Regla

El contrato oficial vive en contracts/, no en docs/.

IIG_Catalogo

IIG_Catalogo es la primera pieza core integrada del sistema catálogo.

Ubicación:

src/catalogo/iig/iig_catalogo.py

Tests:

tests/unit/catalogo/test_iig_catalogo.py

Documentación técnica:

docs/architecture/iig_catalogo.md
Responsabilidades
validar que el registro respeta el contrato formal
validar claves obligatorias
detectar claves extra
validar tipos
validar formatos básicos de fecha y datetime
detectar densidad alta de nulos
generar salida estructurada por registro y por lote
Qué no hace
no corrige
no normaliza
no infiere
no modifica el input
Estado
integrado en GitHub
testeado
operativo dentro de la arquitectura oficial
Modelo territorial multipaís

Orbis Drive no modela un único país.

Modela una arquitectura escalable y agnóstica al país.

Modelo aprobado
T_Paises
↓
T_Subdivisiones_Administrativas
↓
T_Localidades
Principio
Territorio ≠ España

Esto permite:

expansión internacional
coherencia territorial multipaís
reducción de deuda semántica
reutilización de lógica estructural

España se mantiene como primer caso de implementación, pero no condiciona el modelo global.

Estructura del repositorio
orbis-drive/
├── README.md
├── .gitignore
├── docs/
├── db/
├── contracts/
├── src/
├── data/
├── tests/
├── scripts/
└── legacy/
docs/

Reservado a:

manifiesto fundacional
resoluciones oficiales
arquitectura
flujos operativos
criterios de ingestión

Rutas clave:

docs/manifesto/
docs/governance/resoluciones/
docs/architecture/
docs/ingestion/
db/

Reservado a:

esquema SQL
migraciones
seeds ejecutables
documentación técnica del modelo relacional

Regla:

el esquema SQL versionado vive en db/schema/
la base SQLite operativa no se sube a GitHub
contracts/

Reservado a:

contratos formales de datos
definición 1:1 entre dict limpio y esquema
contratos de catálogo y de mercado
src/

Reservado a código fuente.

Subdominios:

src/common/
src/catalogo/
src/mercado/
src/analytics/
data/

Reservado a:

datos ligeros versionables
tablas de verdad auxiliares
muestras controladas
apoyos externos ligeros

Regla:

no subir dumps masivos
no subir bases operativas
tests/

Reservado a:

tests unitarios
tests de integración
tests de contratos
fixtures
scripts/

Reservado a:

setup
validación
mantenimiento
legacy/

Reservado exclusivamente a:

materiales retirados
activos congelados
piezas heredadas

Regla:

legacy nunca se mezcla con el core
Documentos base del sistema

El proyecto dispone de cuatro piezas fundacionales ya reconocidas:

manifiesto fundacional
resolución oficial de ingestión de T_Versiones
resolución oficial de estructura del repositorio
resolución oficial del modelo territorial multipaís

Estas piezas fijan:

arquitectura
gobierno estructural
separación de sistemas
escalabilidad futura
Reglas de versionado y limpieza
Sí deben subirse a GitHub
manifiesto
resoluciones
SQL del esquema
contratos JSON
código fuente
tests
muestras controladas
scripts de validación y mantenimiento
No deben subirse a GitHub
bases SQLite operativas
dumps completos de scraping
outputs pesados
archivos temporales
cachés
credenciales
.env
logs de ejecución no estructurales
Estado actual del sistema

A día de hoy, el repositorio ya contiene:

estructura oficial aprobada
manifiesto y resoluciones en ubicación correcta
contrato formal de T_Versiones
integración de IIG_Catalogo
test unitario operativo para IIG_Catalogo
base preparada para integrar DVL_Catalogo
base preparada para evolución multipaís
Foco inicial

El foco inicial del sistema es:

Seat Ibiza en España

Este foco es operativo, no estructural.
La arquitectura está diseñada desde el inicio para escalar más allá de ese primer caso.

Organización del proyecto

Áreas reconocidas en el sistema:

Dirección General
Dirección de Scraping
Dirección de Base de Datos
Dirección de QA
Dirección de Datos
Dirección de Mercado
Marketing (futuro)
Liderazgo

Proyecto liderado por:

Ignacio Álvarez Cañal
Mensaje final

Orbis Drive no es un repositorio de scripts.

Es una base estructural para construir un sistema de inteligencia de mercado automovilístico robusto, trazable y escalable.
