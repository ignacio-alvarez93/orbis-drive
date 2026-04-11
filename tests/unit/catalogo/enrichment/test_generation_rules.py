from src.catalogo.enrichment.rules.generation_rules import derive_is_current_generation


def test_derive_is_current_generation_true():
    data = {"production_end_year": None}
    result = derive_is_current_generation(data)

    assert result is not None
    assert result["is_current_generation"]["value"] is True


def test_derive_is_current_generation_false():
    data = {"production_end_year": 2017}
    result = derive_is_current_generation(data)

    assert result is not None
    assert result["is_current_generation"]["value"] is False
