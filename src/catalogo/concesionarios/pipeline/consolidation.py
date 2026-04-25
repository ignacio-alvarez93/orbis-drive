from __future__ import annotations

from typing import List

from ..models.concesionario_resolved import ConcesionarioResolved
from .source_priority import get_source_priority


def _score_record(record: ConcesionarioResolved) -> tuple:
    raw = record.validated.normalized.raw
    normalized = record.validated.normalized

    score = (
        get_source_priority(raw.source_name),
        1 if record.localidad_id else 0,
        1 if normalized.website_domain else 0,
        1 if raw.phone_raw else 0,
        1 if raw.address_raw else 0,
        len(raw.description_raw or ""),
    )
    return score


def pick_best_record(records: List[ConcesionarioResolved]) -> ConcesionarioResolved:
    return sorted(records, key=_score_record, reverse=True)[0]