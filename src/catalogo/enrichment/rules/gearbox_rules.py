from __future__ import annotations

from typing import Any, Dict, Optional

from src.catalogo.enrichment.mappers.normalization_maps import GEARBOX_LABEL_KEYWORDS


def derive_gearbox_type(validated_dict: Dict[str, Any]) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    Deriva gearbox_type a partir de gearbox_label con lógica determinista.
    No corrige ni modifica gearbox_label.
    """
    label = validated_dict.get("gearbox_label")

    if not isinstance(label, str) or not label.strip():
        return None

    normalized = label.strip().lower()

    for gearbox_type, keywords in GEARBOX_LABEL_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return {
                "gearbox_type": {
                    "value": gearbox_type,
                    "source": "gearbox_label",
                    "rule": "gearbox_rules.derive_gearbox_type",
                }
            }

    return None
