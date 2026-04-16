from src.catalogo.enrichment.models.enrichment_result import EnrichmentResult
from src.catalogo.enrichment.rules.performance_conversion_rules import derive_max_power_kw
from src.catalogo.enrichment.rules.weight_rules import (
    derive_power_to_weight_cv_ton,
    derive_power_to_weight_kw_ton,
)


def test_derive_power_to_weight_cv_ton():
    row = {"power_cv": 150, "kerb_weight_kg": 1500, "power_to_weight_cv_ton": None}
    result = EnrichmentResult(original_data=row)

    derive_power_to_weight_cv_ton(row, result)

    assert result.enriched_fields["power_to_weight_cv_ton"] == 100.0


def test_derive_power_to_weight_kw_ton():
    row = {
        "max_power_cv": 150,
        "max_power_kw": None,
        "kerb_weight_kg": 1500,
        "power_to_weight_kw_ton": None,
    }
    result = EnrichmentResult(original_data=row)

    derive_max_power_kw(row, result)
    derive_power_to_weight_kw_ton(row, result)

    assert result.enriched_fields["power_to_weight_kw_ton"] == 73.5
