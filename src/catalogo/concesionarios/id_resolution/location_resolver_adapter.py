from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable

from ..models.concesionario_normalized import ConcesionarioNormalized


@dataclass
class LocationResolutionResult:
    pais_id: Optional[str]
    subdivision_id: Optional[str]
    localidad_id: Optional[str]
    is_resolved: bool
    reason: Optional[str] = None


@runtime_checkable
class TerritorialResolverProtocol(Protocol):
    def resolve_concesionario_location(
        self,
        normalized: ConcesionarioNormalized,
    ) -> LocationResolutionResult:
        ...


class LocationResolverAdapter:
    def __init__(self, resolver: TerritorialResolverProtocol) -> None:
        self.resolver = resolver

    def resolve(self, normalized: ConcesionarioNormalized) -> LocationResolutionResult:
        return self.resolver.resolve_concesionario_location(normalized)