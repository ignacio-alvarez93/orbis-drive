from src.catalogo.enrichment.rules.boot_rules import derive_boot_capacity_range


def test_derive_boot_capacity_range():
    data = {"boot_capacity_l": 267}
    result = derive_boot_capacity_range(data)

    assert result is not None
    assert result["boot_capacity_min_l"]["value"] == 267
    assert result["boot_capacity_max_l"]["value"] == 267


def test_derive_boot_capacity_range_returns_none_for_invalid_type():
    assert derive_boot_capacity_range({"boot_capacity_l": "267"}) is None
