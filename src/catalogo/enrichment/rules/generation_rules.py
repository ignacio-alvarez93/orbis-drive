from __future__ import annotations

from typing import Any, Dict, Optional


def derive_is_current_generation(validated_dict: Dict[str, Any]) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    production_end_year = None => generación actual.
    Cualquier valor explícito => False determinista si es entero.
    """
    if "production_end_year" not in validated_dict:
        return None

    end_year = validated_dict.get("production_end_year")

    if end_year is None:
        return {
            "is_current_generation": {
                "value": True,
                "source": "production_end_year",
                "rule": "generation_rules.derive_is_current_generation",
            }
        }

    if isinstance(end_year, int):
        return {
            "is_current_generation": {
                "value": False,
                "source": "production_end_year",
                "rule": "generation_rules.derive_is_current_generation",
            }
        }

    return None
