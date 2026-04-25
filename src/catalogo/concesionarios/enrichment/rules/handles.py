from urllib.parse import urlparse

from ..models import EnrichmentPayload


def _extract_last_path_segment(url: str | None) -> str | None:
    if not url:
        return None

    try:
        parsed = urlparse(url)
        parts = [p for p in parsed.path.split("/") if p]
        if not parts:
            return None
        return parts[-1].strip() or None
    except Exception:
        return None


def enrich_handles(payload: EnrichmentPayload) -> EnrichmentPayload:
    instagram_handle = _extract_last_path_segment(payload.instagram_profile_url)
    tiktok_handle = _extract_last_path_segment(payload.tiktok_profile_url)

    if instagram_handle:
        payload.derived["instagram_handle"] = instagram_handle
        payload.flags["has_instagram_reference"] = True

    if tiktok_handle:
        payload.derived["tiktok_handle"] = tiktok_handle
        payload.flags["has_tiktok_reference"] = True

    if payload.facebook_page_url:
        payload.flags["has_facebook_reference"] = True

    if payload.youtube_channel_url:
        payload.flags["has_youtube_reference"] = True

    if payload.google_business_profile_url:
        payload.flags["has_google_business_profile_reference"] = True

    return payload