from ..models import EnrichmentPayload


DISALLOWED_PLATFORM_DOMAINS = {
    "autocasion.com",
    "www.autocasion.com",
    "coches.net",
    "www.coches.net",
    "abc.es",
    "www.abc.es",
    "mujerhoy.com",
    "www.mujerhoy.com",
    "unoauto.com",
    "www.unoauto.com",
    "autoscout24.es",
    "www.autoscout24.es",
    "rentingcoches.com",
    "www.rentingcoches.com",
}


def enrich_domain(payload: EnrichmentPayload) -> EnrichmentPayload:
    domain = payload.website_domain

    if not domain:
        return payload

    payload.flags["has_website"] = True

    if domain in DISALLOWED_PLATFORM_DOMAINS:
        payload.flags["website_is_platform_or_media"] = True
    else:
        payload.flags["website_is_platform_or_media"] = False
        payload.flags["has_probable_official_website"] = True

    return payload