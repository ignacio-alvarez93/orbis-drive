from src.catalogo.enrichment.rules.gearbox_rules import derive_gearbox_type


def test_derive_gearbox_type_manual():
    data = {"gearbox_label": "5 Velocidades"}
    result = derive_gearbox_type(data)

    assert result is not None
    assert result["gearbox_type"]["value"] == "manual"


def test_derive_gearbox_type_automatic():
    data = {"gearbox_label": "7 velocidades DSG"}
    result = derive_gearbox_type(data)

    assert result is not None
    assert result["gearbox_type"]["value"] == "automatic"


def test_derive_gearbox_type_returns_none_when_empty():
    assert derive_gearbox_type({"gearbox_label": None}) is None
