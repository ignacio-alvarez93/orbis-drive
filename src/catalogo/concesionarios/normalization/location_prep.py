from typing import List

from .canonicalizers import basic_clean, collapse_spaces


def build_location_candidates(address_raw: str | None,
                              postal_code_raw: str | None,
                              location_raw: str | None) -> List[str]:
    candidates: List[str] = []

    for value in [address_raw, postal_code_raw, location_raw]:
        cleaned = basic_clean(value)
        if cleaned:
            candidates.append(cleaned)

    if address_raw and location_raw:
        merged = collapse_spaces(f"{address_raw} {location_raw}")
        if merged not in candidates:
            candidates.append(merged)

    return candidates