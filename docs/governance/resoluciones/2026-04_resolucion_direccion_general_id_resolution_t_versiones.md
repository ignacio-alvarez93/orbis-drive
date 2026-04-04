
RESOLUCIÓN DE DIRECCIÓN GENERAL
Activación de la capa de resolución de identidad para T_Versiones

Proyecto: Orbis Drive
Fecha: Abril 2026
Estado: 🚀 APROBADO — IDENTIDAD PERSISTIBLE HABILITADA

1. RESUMEN EJECUTIVO

Tras la revisión del primer lote piloto de ingestión de T_Versiones y del esquema físico actual de base
de datos, se determina la necesidad de incorporar una capa formal de resolución de identidad previa a
la ingestión.

Se aprueba por tanto la activación del componente:

👉 ID_RESOLUTION_T_VERSIONES

2. PROBLEMA DETECTADO

El sistema de validación actual es capaz de producir datos semánticamente correctos, pero el lote piloto
validado no incorpora todavía las identidades persistibles exigidas por la base de datos.

La SQLite actual exige:

- manufacturer_id
- model_id
- generation_id
- version_id

y establece además:

- generation_id como obligatorio en T_Versiones
- unicidad por (version_name_canonical, generation_id)

3. DECISIÓN

Se establece como norma oficial:

👉 la base de datos no resuelve identidad
👉 la base de datos persiste identidad ya resuelta

Por tanto, la ingestión de T_Versiones solo podrá ejecutarse cuando el dataset haya superado también la
resolución formal de identidad.

4. POSICIÓN EN EL FLUJO

El flujo oficial pasa a quedar definido como:

SCRAPER → DICT LIMPIO → IIG → DVL → VALIDACIÓN DE LOTE → ID RESOLUTION → INGESTIÓN

5. PRINCIPIOS CONSOLIDADOS

Esta capa refuerza:

- no inferencia en DB
- trazabilidad completa
- robustez sobre velocidad
- persistencia solo de verdad formalizada

6. REGLAS OPERATIVAS

La capa de ID Resolution debe:

- reutilizar identidades existentes en DB
- rechazar registros sin jerarquía resoluble
- generar version_id y version_name_canonical de forma determinista
- no crear fabricantes, modelos ni generaciones de forma automática en esta fase piloto

7. IMPACTO EN EL SISTEMA

Con esta decisión, Orbis Drive completa el paso que separa:

dato válido
de
dato persistible

8. ESTADO FINAL

✅ ID Resolution aprobada
✅ Flujo de ingestión reforzado
✅ T_Versiones preparada para persistencia controlada

MENSAJE FINAL

“La verdad validada aún no basta.

Debe poder ser identificada sin ambigüedad antes de entrar en la base.”

Dirección General
Proyecto Orbis Drive
