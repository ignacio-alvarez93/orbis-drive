from typing import List

from ..models.concesionario_resolved import ConcesionarioResolved
from ..models.concesionario_validated import ConcesionarioValidated
from .location_resolver_adapter import (
    LocationResolverAdapter,
    TerritorialResolverProtocol,
)
from .semantic_key import build_semantic_key, build_concesionario_id


class IDResolutionConcesionarios:
    def __init__(self, resolver: TerritorialResolverProtocol) -> None:
        self.adapter = LocationResolverAdapter(resolver)

    def resolve_record(self, validated: ConcesionarioValidated) -> ConcesionarioResolved:
        resolution = self.adapter.resolve(validated.normalized)

        semantic_key = None
        concesionario_id = None

        if resolution.is_resolved:
            semantic_key = build_semantic_key(
                validated=validated,
                localidad_id=resolution.localidad_id,
            )
            concesionario_id = build_concesionario_id(semantic_key)
        else:
            validated.is_valid = False
            validated.classification_status = "PENDIENTE"
            if resolution.reason:
                validated.validation_warnings.append(
                    f"id_resolution_pending: {resolution.reason}"
                )

        return ConcesionarioResolved(
            validated=validated,
            pais_id=resolution.pais_id,
            subdivision_id=resolution.subdivision_id,
            localidad_id=resolution.localidad_id,
            semantic_key_concesionario=semantic_key,
            concesionario_id=concesionario_id,
        )

    def batch_resolve(
        self,
        validated_records: List[ConcesionarioValidated],
    ) -> List[ConcesionarioResolved]:
        return [self.resolve_record(record) for record in validated_records]