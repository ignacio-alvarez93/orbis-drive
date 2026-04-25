from typing import List

from .models import EnrichmentPayload
from .rules.domains import enrich_domain
from .rules.handles import enrich_handles
from .rules.quality_flags import enrich_quality_flags
from ..models.concesionario_resolved import ConcesionarioResolved


class EnrichmentConcesionariosEngine:
    @classmethod
    def enrich_record(cls, resolved: ConcesionarioResolved) -> EnrichmentPayload:
        raw = resolved.validated.normalized.raw
        normalized = resolved.validated.normalized

        payload = EnrichmentPayload(
            resolved=resolved,
            telefono=raw.phone_raw,
            email=raw.email_raw,
            website_url=raw.website_raw,
            website_domain=normalized.website_domain,
            instagram_profile_url=raw.instagram_raw,
            facebook_page_url=raw.facebook_raw,
            tiktok_profile_url=raw.tiktok_raw,
            youtube_channel_url=raw.youtube_raw,
            google_business_profile_url=raw.google_business_profile_raw,
            direccion_texto=normalized.direccion_texto_normalizada,
            codigo_postal=normalized.codigo_postal_normalizado,
            ubicacion_raw=raw.location_raw,
            description_raw=raw.description_raw,
            brands_raw=raw.brands_raw,
        )

        payload = enrich_domain(payload)
        payload = enrich_handles(payload)
        payload = enrich_quality_flags(payload)

        return payload

    @classmethod
    def batch_enrich(cls, resolved_records: List[ConcesionarioResolved]) -> List[EnrichmentPayload]:
        return [cls.enrich_record(record) for record in resolved_records]