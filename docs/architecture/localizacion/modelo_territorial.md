# Modelo territorial — T_Localizacion

## Proyecto
Orbis Drive

## Estado
Borrador operativo alineado con resolución oficial multipaís

## Base de diseño

Este modelo territorial se diseña conforme a los principios fundacionales de Orbis Drive:

- separación de responsabilidades
- mejor NULL que dato incorrecto
- no inferencia
- trazabilidad completa
- robustez sobre velocidad

Y conforme a la resolución de rediseño territorial multipaís, que establece que el modelo territorial del sistema no puede depender de la estructura administrativa de un país concreto. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1}

---

# 1. Objetivo del modelo

`T_Localizacion` es el pilar estructural encargado de representar territorio de forma operativa, multipaís y escalable dentro de Orbis Drive.

Su misión es permitir que el sistema:

- funcione inicialmente con España
- absorba nuevos países sin refactorización
- soporte jerarquías administrativas variables
- sirva como base futura de Orbis-Mundus
- pueda operar de forma autónoma sin depender de Mundus

---

# 2. Principio rector

Orbis Drive no modela España.

Orbis Drive modela territorio global empezando por España.

Esto implica:

- no crear tablas específicas por país
- no fijar nombres administrativos nacionales como parte de la arquitectura
- no asumir profundidad jerárquica fija
- no duplicar niveles territoriales en tablas separadas

---

# 3. Estructura oficial del modelo

El modelo territorial oficial se define así:

```text
T_Paises
↓
T_Subdivisiones_Administrativas
↓
T_Localidades