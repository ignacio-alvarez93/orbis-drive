from src.catalogo.enrichment.rules.trim_rules import derive_trim_from_version_name


def test_derive_trim_from_version_name():
    data = {"version_name": "1.0 MPI 80CV Reference"}
    result = derive_trim_from_version_name(data)

    assert result is not None
    assert result["trim"]["value"] == "Reference"


def test_derive_trim_from_version_name_returns_none_when_no_explicit_trim():
    data = {"version_name": "1.9 TDI 105CV"}
    assert derive_trim_from_version_name(data) is None
