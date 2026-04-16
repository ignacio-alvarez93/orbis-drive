from src.catalogo.enrichment.models.enrichment_result import EnrichmentResult
from src.catalogo.enrichment.rules.efficiency_rules import (
    derive_fuel_consumption_combined_mpg_uk,
    derive_fuel_consumption_combined_mpg_us,
)


def test_derive_fuel_consumption_combined_mpg_uk():
    row = {
        "fuel_consumption_combined_l_100km": 5.0,
        "fuel_consumption_combined_mpg_uk": None,
    }
    result = EnrichmentResult(original_data=row)

    derive_fuel_consumption_combined_mpg_uk(row, result)

    assert result.enriched_fields["fuel_consumption_combined_mpg_uk"] == 56.5


def test_derive_fuel_consumption_combined_mpg_us():
    row = {
        "fuel_consumption_combined_l_100km": 5.0,
        "fuel_consumption_combined_mpg_us": None,
    }
    result = EnrichmentResult(original_data=row)

    derive_fuel_consumption_combined_mpg_us(row, result)

    assert result.enriched_fields["fuel_consumption_combined_mpg_us"] == 47.0
