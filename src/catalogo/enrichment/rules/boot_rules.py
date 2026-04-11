from __future__ import annotations

from typing import Any, Dict, Optional


def derive_boot_capacity_range(validated_dict: Dict[str, Any]) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    Si boot_capacity_l existe como valor simple, lo explicita como min y max.
    """
    boot_capacity = validated_dict.get("boot_capacity_l")

    if boot_capacity is None:
        return None

    if not isinstance(boot_capacity, (int, float)):
        return None

    value = int(boot_capacity)

    return {
        "boot_capacity_min_l": {
            "value": value,
            "source": "boot_capacity_l",
            "rule": "boot_rules.derive_boot_capacity_range",
        },
        "boot_capacity_max_l": {
            "value": value,
            "source": "boot_capacity_l",
            "rule": "boot_rules.derive_boot_capacity_range",
        },
    }
