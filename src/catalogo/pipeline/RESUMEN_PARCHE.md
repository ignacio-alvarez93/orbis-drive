# Resumen corto del parche

## Antes
```python
self._prevalidate_row(row, idx)
refs = self.resolver.resolve_all(row)
result = self.loader.insert_one(... row=row, refs=refs ...)
```

## Después
```python
self._prevalidate_row(row, idx)
row_for_resolution, enrichment_payload = self._build_row_for_resolution(row)
refs = self.resolver.resolve_all(row_for_resolution)
result = self.loader.insert_one(... row=row_for_resolution, refs=refs ...)
```

## Motivo

`ENRICHMENT` debe ejecutarse después de VALIDACIÓN DE LOTE y antes de ID_RESOLUTION,
sin mutar la verdad base del registro.
