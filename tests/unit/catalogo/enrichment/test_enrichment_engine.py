from src.catalogo.enrichment.core.enrichment_engine import EnrichmentEngine


def test_engine_runs_all_rules_and_preserves_input():
    original = {
        "version_name": "1.0 MPI 80CV Reference",
        "gearbox_label": "5 Velocidades",
        "boot_capacity_l": 267,
        "production_end_year": None,
    }

    snapshot = dict(original)

    engine = EnrichmentEngine()
    result = engine.run(original)

    assert original == snapshot
    assert result.original_data == snapshot

    assert result.enriched_fields["gearbox_type"] == "manual"
    assert result.enriched_fields["boot_capacity_min_l"] == 267
    assert result.enriched_fields["boot_capacity_max_l"] == 267
    assert result.enriched_fields["trim"] == "Reference"
    assert result.enriched_fields["is_current_generation"] is True

    assert "gearbox_type" in result.trace
    assert result.trace["gearbox_type"]["source"] == "gearbox_label"
    assert result.metrics["enriched_fields_count"] == 5


def test_engine_does_not_overwrite_existing_fields():
    original = {
        "gearbox_label": "5 Velocidades",
        "gearbox_type": "manual",
    }

    engine = EnrichmentEngine()
    result = engine.run(original)

    assert result.enriched_fields == {}
