📄 RESOLUCIÓN DE DIRECCIÓN GENERAL
Estructura oficial del repositorio de Orbis Drive

Proyecto: Orbis Drive
Área emisora: Dirección General
Destinatarios: Todas las áreas del proyecto
Fecha: Marzo 2026
Estado: 🚀 APROBADO — FUENTE OFICIAL DEL PROYECTO

1. Resumen ejecutivo

Tras la auditoría estructural del repositorio y en coherencia con el manifiesto fundacional de Orbis Drive, se aprueba la estructura oficial de GitHub como representación formal del sistema. El proyecto se define como una plataforma de inteligencia de mercado automovilístico, con foco inicial en Seat Ibiza en España, basada en la arquitectura SCRAPERS → DICT LIMPIO → IIG → DVL → PIPELINE → BASE DE DATOS → ANALÍTICA.

Asimismo, se mantiene como norma oficial la separación obligatoria entre Sistema Catálogo y Sistema Mercado, ya fijada para la ingestión de T_Versiones, donde T_Versiones se considera tabla de verdad semántica del vehículo y su flujo propio queda formalmente aislado del flujo de T_Anuncios.

2. Principio rector

Se establece como norma del sistema:

El repositorio de GitHub de Orbis Drive es la fuente única de verdad estructural del proyecto.

Esto implica que el repositorio debe reflejar con exactitud:

la arquitectura del sistema
las responsabilidades por capa
los contratos de datos
la documentación oficial
la separación entre catálogo y mercado
3. Estructura oficial aprobada

Se aprueba como estructura base oficial del repositorio la siguiente:

orbis-drive/
├── README.md
├── .gitignore
├── LICENSE
├── docs/
│   ├── manifesto/
│   ├── governance/
│   ├── architecture/
│   └── ingestion/
├── db/
│   ├── schema/
│   ├── migrations/
│   ├── seeds/
│   └── docs/
├── contracts/
│   ├── catalogo/
│   ├── mercado/
│   └── README.md
├── src/
│   ├── common/
│   ├── catalogo/
│   ├── mercado/
│   └── analytics/
├── data/
│   ├── truth/
│   ├── samples/
│   └── external/
├── tests/
├── scripts/
└── legacy/
4. Reglas oficiales de ubicación
4.1 docs/

Reservado a:

manifiesto fundacional
resoluciones oficiales
arquitectura
flujos operativos
criterios de ingestión
Ubicaciones aprobadas
docs/manifesto/orbis_drive_manifesto.pdf
docs/governance/resoluciones/
docs/architecture/
docs/ingestion/

El manifiesto fundacional y la resolución oficial de T_Versiones quedan reconocidos como documentos base del sistema.

4.2 db/

Reservado a:

esquema SQL
migraciones
seeds ejecutables de base de datos
documentación técnica del modelo relacional
Regla

El esquema SQL versionado vive en db/schema/.

La base SQLite operativa no debe subirse a GitHub.

4.3 contracts/

Reservado a:

contratos formales de datos
definición 1:1 entre dict_limpio y esquema
contratos de catálogo y de mercado
Regla

El contrato oficial del sistema vive en contracts/, no en docs/.

4.4 src/

Reservado a código fuente.

Separación obligatoria
src/catalogo/ → sistema de catálogo
src/mercado/ → sistema de mercado

Esto da cumplimiento directo a la norma ya aprobada de que T_Versiones y T_Anuncios no comparten pipeline ni capas operativas.

4.5 data/

Reservado a:

tablas de verdad y catálogos ligeros versionables
muestras controladas
datos externos de apoyo
Regla

No deben subirse dumps masivos ni bases operativas.

4.6 legacy/

Reservado exclusivamente a:

materiales retirados
activos congelados
piezas heredadas de Mercado Ibiza
Regla

Legacy nunca se mezcla con el core.

5. Ajustes obligatorios de cierre

Se establecen como ajustes definitivos sobre la auditoría:

5.1 Seeds

No se duplicarán en db/ y data/.

Decisión
db/seeds/ = seeds ejecutables
data/ = datos versionables ligeros
5.2 Contratos

contracts/ será la fuente oficial del contrato de datos.

Decisión
contracts/ = contrato operativo
docs/ = documentación explicativa
5.3 Esquema SQL

db/schema/ deberá incluir un README.md con el orden oficial de ejecución del esquema.

6. Archivos que sí deben subirse a GitHub

Se aprueba subir:

manifiesto
resoluciones
SQL del esquema
contratos JSON
código fuente
tests
muestras controladas
scripts de validación y mantenimiento
7. Archivos que no deben subirse a GitHub

Queda prohibido subir:

bases SQLite operativas
dumps completos de scraping
outputs pesados
archivos temporales
cachés
credenciales
.env
logs de ejecución no estructurales
8. Principio de separación estructural

Se consolida como norma oficial:

Catálogo ≠ Mercado

y, por tanto:

src/catalogo ≠ src/mercado
IIG_Catalogo ≠ IIG_Mercado
DVL_Catalogo ≠ DVL_Mercado

Esto queda alineado con la resolución fundacional de ingestión de T_Versiones.

9. Estado final

Con esta resolución, Orbis Drive dispone ya de:

manifiesto fundacional
flujo oficial de ingestión de T_Versiones
estructura oficial del repositorio
separación entre gobierno, contratos, base de datos, código y datos
10. Resolución final
✅ ESTRUCTURA DEL REPOSITORIO APROBADA
✅ GITHUB DECLARADO FUENTE ÚNICA DE VERDAD ESTRUCTURAL
✅ RESOLUCIÓN OFICIAL DEL PROYECTO

Dirección General
Proyecto Orbis Drive