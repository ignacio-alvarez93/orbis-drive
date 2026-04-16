from src.catalogo.enrichment.models.enrichment_result import EnrichmentResult
from src.catalogo.enrichment.rules.performance_conversion_rules import (
    derive_max_power_kw,
    derive_specific_output_kw_l,
    derive_top_speed_mph,
)


def test_derive_max_power_kw():
    row = {"max_power_cv": 150, "max_power_kw": None}
    result = EnrichmentResult(original_data=row)

    derive_max_power_kw(row, result)

    assert result.enriched_fields["max_power_kw"] == 110.3


def test_derive_specific_output_kw_l():
    row = {
        "max_power_cv": 150,
        "max_power_kw": None,
        "engine_displacement_l": 2.0,
        "specific_output_kw_l": None,
    }
    result = EnrichmentResult(original_data=row)

    derive_max_power_kw(row, result)
    derive_specific_output_kw_l(row, result)

    assert result.enriched_fields["specific_output_kw_l"] == 55.1


def test_derive_top_speed_mph():
    row = {"top_speed_kmh": 200, "top_speed_mph": None}
    result = EnrichmentResult(original_data=row)

    derive_top_speed_mph(row, result)

    assert result.enriched_fields["top_speed_mph"] == 124.3
