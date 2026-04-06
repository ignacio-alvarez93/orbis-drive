Sustituye:
src/catalogo/loaders/t_versiones_loader.py

Este loader v2:
- mantiene anti-duplicado por (version_name_canonical, generation_id)
- inserta todas las columnas reales de T_Versiones presentes en el dict
- usa PRAGMA table_info para alinearse con el schema real
