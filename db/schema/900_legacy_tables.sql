-- Orbis Drive
-- Schema generado desde Orbis_Drive.db
-- Bloque 900: tablas auxiliares/legacy detectadas en la SQLite actual

PRAGMA foreign_keys = ON;

CREATE TABLE "seat_ibiza_generaciones" (
	"manufacturer_id"	TEXT,
	"manufacturer_name"	TEXT,
	"manufacturer_name_upper"	TEXT,
	"model_id"	TEXT,
	"model_name"	TEXT,
	"model_name_upper"	TEXT,
	"generation_id"	TEXT,
	"generation_name"	TEXT,
	"generation_name_canonical"	TEXT,
	"generation_name_upper"	TEXT,
	"year_start"	INTEGER,
	"year_end"	TEXT,
	"year_end_raw"	TEXT,
	"generation_href_relative"	TEXT,
	"generation_href_absolute"	TEXT
);
