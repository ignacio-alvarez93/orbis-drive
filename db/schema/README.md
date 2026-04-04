# db/schema generado desde `Orbis_Drive.db`

Este paquete contiene una **extracción versionable** del esquema detectado en la base SQLite subida a la conversación.

## Orden de ejecución

1. `001_core_tables.sql`
2. `002_mercado_tables.sql`
3. `003_territorio_tables.sql`
4. `900_legacy_tables.sql` (solo si se quiere conservar la tabla auxiliar detectada)
5. `004_constraints_indexes.sql`

## Alcance

Incluye las tablas detectadas en la SQLite actual:

- `T_Fabricantes`
- `T_Modelos`
- `T_Generaciones`
- `T_Versiones`
- `T_Concesionarios`
- `T_Anuncios`
- `T_Historico_Precios`
- `T_Paises`
- `T_Provincias`
- `T_Municipios`
- `seat_ibiza_generaciones`

## Advertencia importante

Esta extracción refleja fielmente la **estructura física actual** de la SQLite subida, pero **no sustituye** la validación arquitectónica oficial.

En particular:

- el repositorio oficial fija `db/schema/` como ubicación del SQL versionado;
- la base operativa no debe ser la fuente canónica única;
- el modelo territorial aprobado por resolución es multipaís y reemplaza el esquema legado `T_Paises -> T_Provincias -> T_Municipios` por un diseño más general.

Por tanto, estos ficheros sirven como:

- base de trabajo inmediata para versionar el esquema;
- referencia de recuperación si Base de Datos aún no ha entregado el SQL formal;
- punto de partida para una posterior normalización del bloque territorial.
