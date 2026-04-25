from typing import List, Tuple

from ..models.concesionario_raw_record import ConcesionarioRawRecord


class IIGConcesionarios:

    REQUIRED_FIELDS = [
        "record_external_id",
        "dealer_name_raw",
        "location_raw",
        "source_name",
        "source_url",
        "source_row_url",
        "scrape_date",
    ]

    @classmethod
    def validate(cls, record: ConcesionarioRawRecord) -> Tuple[bool, List[str]]:
        errors = []

        for field in cls.REQUIRED_FIELDS:
            value = getattr(record, field, None)

            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"{field} es obligatorio")

        if record.brands_raw is not None and not isinstance(record.brands_raw, list):
            errors.append("brands_raw debe ser lista o null")

        return (len(errors) == 0, errors)

    @classmethod
    def batch_validate(cls, records: List[ConcesionarioRawRecord]):
        valid = []
        rejected = []

        for r in records:
            ok, errors = cls.validate(r)

            if ok:
                valid.append(r)
            else:
                rejected.append((r, errors))

        return valid, rejected