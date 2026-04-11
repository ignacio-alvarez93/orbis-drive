from __future__ import annotations

from typing import Any, Dict, Optional


KNOWN_TRIMS = [
    "reference",
    "style",
    "style plus",
    "fr",
    "fr go",
    "xcellence",
    "xcellence go",
    "sport",
    "sport limited",
    "excellence",
    "urban",
    "business",
    "s line",
    "amg line",
    "advance",
]


def derive_trim_from_version_name(validated_dict: Dict[str, Any]) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    Extrae trim solo cuando aparece como sufijo explícito en version_name.
    Evita inferencias agresivas.
    """
    version_name = validated_dict.get("version_name")

    if not isinstance(version_name, str) or not version_name.strip():
        return None

    normalized = " ".join(version_name.lower().split())

    matched_trim = None
    for trim in sorted(KNOWN_TRIMS, key=len, reverse=True):
        if normalized.endswith(trim):
            matched_trim = trim
            break

    if not matched_trim:
        return None

    return {
        "trim": {
            "value": matched_trim.title(),
            "source": "version_name",
            "rule": "trim_rules.derive_trim_from_version_name",
        }
    }
