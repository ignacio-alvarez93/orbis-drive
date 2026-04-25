from collections import defaultdict
from typing import Dict, List, Tuple

from ...models.concesionario_resolved import ConcesionarioResolved


def detect_duplicates(
    records: List[ConcesionarioResolved],
) -> Tuple[Dict[str, List[ConcesionarioResolved]], List[str]]:
    by_semantic_key: Dict[str, List[ConcesionarioResolved]] = defaultdict(list)
    warnings: List[str] = []

    for record in records:
        key = record.semantic_key_concesionario
        if key:
            by_semantic_key[key].append(record)

    duplicate_groups = {
        key: group
        for key, group in by_semantic_key.items()
        if len(group) > 1
    }

    for key, group in duplicate_groups.items():
        sources = sorted({item.validated.normalized.raw.source_name for item in group})
        warnings.append(
            f"duplicate semantic_key={key} count={len(group)} sources={sources}"
        )

    return duplicate_groups, warnings