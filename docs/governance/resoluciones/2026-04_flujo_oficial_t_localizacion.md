RESOLUCIÓN DE DIRECCIÓN GENERAL
Flujo oficial del sistema de localización — T_Localizacion

Proyecto: Orbis Drive
Fecha: Abril 2026
Estado: 🚀 APROBADO — MARCO OPERATIVO OFICIAL DEL PILAR TERRITORIAL

1. RESUMEN EJECUTIVO

Tras la consolidación del sistema catálogo de Orbis Drive y la activación de la fase de construcción de pilares estructurales, se aprueba el flujo oficial del sistema de localización:

👉 T_Localizacion

como pilar territorial autónomo del proyecto.

Este sistema tendrá como función:

representar territorio de forma estructurada
operar inicialmente con España
escalar sin refactorización a nuevos países
servir como base de localización para futuros sistemas de mercado
permitir evolución futura hacia integración o potenciación con Orbis-Mundus
2. CONTEXTO ESTRATÉGICO

Dirección General ya ha establecido que:

Orbis Drive no puede depender de un modelo territorial sesgado a España
el sistema territorial debe ser multipaís
la fase actual del proyecto exige construir pilares estructurales antes del sistema de mercado

En coherencia con ello, se declara que:

👉 T_Localizacion no es una tabla auxiliar
👉 T_Localizacion es un sistema territorial formal del proyecto

3. PRINCIPIO FUNDAMENTAL

Se establece como norma del sistema:

el dato territorial no entra por confianza, entra por verificación formal

Esto implica que toda carga territorial deberá seguir un pipeline explícito, trazable y validable, del mismo modo que ya ocurre en T_Versiones.

4. MODELO TERRITORIAL OFICIAL

Se ratifica como estructura oficial del sistema territorial:

T_Paises
↓
T_Subdivisiones_Administrativas
↓
T_Localidades

Este modelo:

no depende de la estructura administrativa de un país concreto
no fija nombres nacionales como parte de la arquitectura
no asume profundidad jerárquica fija
permite representación multipaís escalable

Se refuerza el principio:

Orbis Drive no modela España. Orbis Drive modela territorio global empezando por España.

5. FLUJO OFICIAL APROBADO

Se establece como flujo oficial del sistema de localización:

CSV
→ STAGING
→ IIG_Localizacion
→ NORMALIZACION_TERRITORIAL
→ DVL_Localizacion
→ VALIDACION_LOTE_Localizacion
→ ID_RESOLUTION_Localizacion
→ INGESTION
→ REPORTE

Este flujo pasa a ser:

👉 obligatorio
👉 único flujo autorizado para ingestión territorial controlada

6. JUSTIFICACIÓN DE LA NUEVA CAPA DE NORMALIZACIÓN

Se aprueba formalmente la incorporación de una capa específica:

👉 NORMALIZACION_TERRITORIAL

Motivo:

el dato territorial de entrada puede venir expresado en formas heterogéneas, nacionales o dependientes de fuente, mientras que el sistema interno de Orbis Drive exige una representación jerárquica genérica, multipaís y semánticamente consistente.

Por tanto, la normalización territorial es necesaria para:

traducir input de fuente al modelo territorial oficial
resolver variantes controladas de nombres
asignar nivel administrativo
preparar relaciones jerárquicas candidatas
desacoplar el sistema de la forma concreta de entrada
7. DELIMITACIÓN OFICIAL DE RESPONSABILIDADES
7.1 STAGING

Función:

👉 recepción estructurada del dato de entrada

Debe:

cargar CSV
homogeneizar formato básico
conservar trazabilidad de archivo y fila
preparar payload bruto para validación

No puede:

validar semántica
inferir jerarquía
corregir territorio
7.2 IIG_Localizacion

Estado: OBLIGATORIO — MODO ESTRICTO

Función:

👉 guardián estructural del contrato territorial

Debe:

validar esquema exacto
validar campos obligatorios
validar tipos
rechazar desviaciones estructurales

No puede:

modificar datos
mapear nombres
deducir jerarquías
inferir valores ausentes
7.3 NORMALIZACION_TERRITORIAL

Estado: OBLIGATORIA

Función:

👉 traducir el dato territorial de entrada al modelo territorial interno de Orbis Drive

Permitido:

canonicalización controlada de nombres
normalización de labels administrativos
asignación de nivel territorial
preparación de claves semánticas territoriales
resolución de equivalencias explícitas y trazables

Prohibido:

inventar entidades
inferir país o jerarquía sin base
completar datos ausentes arbitrariamente
alterar la verdad fuente sin trazabilidad
7.4 DVL_Localizacion

Estado: OBLIGATORIA — MODO CONSERVADOR

Función:

👉 validación de coherencia territorial

Debe:

validar que la jerarquía sea coherente
validar pertenencia correcta entre país, subdivisión y localidad
detectar contradicciones entre código, nombre y nivel
bloquear combinaciones territoriales imposibles o incoherentes

No puede:

reconstruir jerarquía de forma agresiva
corregir conflictos automáticamente
aceptar incoherencias por conveniencia operativa
7.5 VALIDACION_LOTE_Localizacion

Estado: OBLIGATORIA

Función:

👉 validación global del dataset territorial

Debe garantizar:

ausencia de duplicados
unicidad semántica territorial
consistencia global del lote
ausencia de colisiones jerárquicas
cobertura estructural del dataset
7.6 ID_RESOLUTION_Localizacion

Estado: OBLIGATORIA PREVIA A INGESTIÓN

Función:

👉 resolver identidad persistible del dato territorial validado

Debe:

resolver pais_id
resolver subdivision_id
resolver parent_id
preparar identidad persistible para T_Localidades
bloquear inserción si la identidad no puede resolverse de forma explícita

Principio:

👉 validación del dato y persistencia del dato son responsabilidades separadas

7.7 INGESTION

Función:

👉 persistencia controlada exclusivamente de registros que hayan superado todas las capas anteriores

Condición obligatoria:

solo podrá insertarse dato que haya superado:

IIG
NORMALIZACION
DVL
VALIDACIÓN DE LOTE
ID_RESOLUTION
7.8 REPORTE

Función:

👉 trazabilidad completa de cada ejecución

Debe incluir:

procesados
válidos
rechazados estructurales
rechazados semánticos
rechazados de lote
fallos de resolución de identidad
insertados
incidencias detectadas
8. PRINCIPIOS DE DISEÑO CONSOLIDADOS

Este flujo debe cumplir estrictamente con los principios fundacionales del sistema:

separación de responsabilidades
mejor NULL que dato incorrecto
no inferencia
trazabilidad completa
robustez sobre velocidad
9. RELACIÓN CON ORBIS-MUNDUS

Se establece de forma expresa:

👉 T_Localizacion se desarrolla como sistema autónomo dentro de Orbis Drive

Pero además:

👉 debe diseñarse para poder ser ampliado, reutilizado o potenciado en el futuro por sistemas territoriales superiores del ecosistema, incluyendo Orbis-Mundus

Esto implica:

independencia funcional en Orbis Drive
compatibilidad conceptual con evolución multipaís
ausencia de acoplamientos a España como caso fijo
arquitectura preparada para reutilización futura
10. ORDEN OPERATIVO DE IMPLEMENTACIÓN

Se establece como secuencia oficial de ejecución:

Fase 1

T_Paises

Fase 2

T_Subdivisiones_Administrativas

Fase 3

T_Localidades

Cada una deberá ejecutarse bajo el mismo flujo aprobado y respetando dependencias jerárquicas de identidad y persistencia.

11. RESTRICCIONES CRÍTICAS

Queda expresamente prohibido:

cargar territorio saltando capas
usar DVL como sustituto de normalización
fijar arquitectura dependiente de España
introducir tablas específicas por país
inferir jerarquías no explícitas
insertar registros sin identidad persistible resuelta
12. IMPACTO EN EL SISTEMA

La aprobación de este flujo habilita:

construcción formal del pilar territorial
base geográfica coherente para mercado
expansión controlada a nuevos países
trazabilidad territorial completa
preparación futura para integración con sistemas horizontales del ecosistema
13. CAMBIO DE NIVEL DEL PROYECTO

Se establece oficialmente:

👉 Orbis Drive deja de limitarse al catálogo técnico

y pasa a consolidar:

👉 una infraestructura estructural del mundo real, comenzando por territorio

14. MENSAJE FINAL

“El territorio no es un dato auxiliar.

Es una estructura de verdad que debe validarse con la misma disciplina con la que se valida el vehículo.”

RESOLUCIÓN FINAL

✅ FLUJO OFICIAL DE T_LOCALIZACION APROBADO
✅ NORMALIZACION_TERRITORIAL INCORPORADA FORMALMENTE
✅ PILAR TERRITORIAL DECLARADO SISTEMA AUTÓNOMO Y ESCALABLE
🚀 ORBIS DRIVE AUTORIZADO A IMPLEMENTAR EL SISTEMA DE LOCALIZACIÓN BAJO CONTROL ESTRICTO

Dirección General
Proyecto Orbis Drive