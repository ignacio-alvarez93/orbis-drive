# Ejemplo de integración en pipeline

Este parche es orientativo. Ajusta nombres según tu `src/catalogo/pipeline/ingestion_pipeline.py`.

```python
from src.catalogo.enrichment.core.enrichment_engine import EnrichmentEngine

enrichment_engine = EnrichmentEngine()

for validated_dict in validated_records:
    enrichment_result = enrichment_engine.run(validated_dict)

    payload_for_resolution = {
        **validated_dict,
        **enrichment_result.enriched_fields,
    }

    resolved_record = id_resolver.resolve(payload_for_resolution)

    audit_entry = {
        "validated": validated_dict,
        "enrichment": enrichment_result.to_dict(),
        "resolved": resolved_record,
    }
```

## Recomendaciones

- Mantén `validated_dict` intacto
- Usa `payload_for_resolution` como vista operativa
- Guarda `trace` para auditoría
- No mezcles enriquecimiento con validación
