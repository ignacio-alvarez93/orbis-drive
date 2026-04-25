from ..models import EnrichmentPayload


def enrich_quality_flags(payload: EnrichmentPayload) -> EnrichmentPayload:
    payload.flags["has_contact"] = any([
        payload.telefono,
        payload.email,
        payload.website_url,
    ])

    payload.flags["has_full_address"] = all([
        payload.direccion_texto,
        payload.codigo_postal,
        payload.ubicacion_raw,
    ])

    payload.flags["has_social_reference"] = any([
        payload.instagram_profile_url,
        payload.facebook_page_url,
        payload.tiktok_profile_url,
        payload.youtube_channel_url,
        payload.google_business_profile_url,
    ])

    payload.flags["has_description"] = bool(payload.description_raw)
    payload.flags["has_brands"] = bool(payload.brands_raw)

    return payload