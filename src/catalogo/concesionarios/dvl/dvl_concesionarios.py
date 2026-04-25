from typing import List

from ..models.concesionario_normalized import ConcesionarioNormalized
from ..models.concesionario_validated import ConcesionarioValidated
from .rules.identity_rules import validate_identity
from .rules.contact_rules import validate_contact
from .rules.commercial_actor_rules import validate_commercial_actor


class DVLConcesionarios:

    @classmethod
    def validate_record(cls, normalized: ConcesionarioNormalized) -> ConcesionarioValidated:
        errors: List[str] = []
        warnings: List[str] = []

        errors.extend(validate_identity(normalized))
        errors.extend(validate_commercial_actor(normalized))
        warnings.extend(validate_contact(normalized))

        if errors:
            classification_status = "RECHAZADO"
            is_valid = False
        else:
            if not normalized.location_candidates:
                classification_status = "PENDIENTE"
                is_valid = False
                warnings.append("sin candidatos de localizacion")
            else:
                classification_status = "INGESTABLE"
                is_valid = True

        return ConcesionarioValidated(
            normalized=normalized,
            is_valid=is_valid,
            validation_errors=errors,
            validation_warnings=warnings,
            classification_status=classification_status,
        )

    @classmethod
    def batch_validate(cls, normalized_records: List[ConcesionarioNormalized]) -> List[ConcesionarioValidated]:
        return [cls.validate_record(record) for record in normalized_records]