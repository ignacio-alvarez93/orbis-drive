import re
from typing import Optional
from urllib.parse import urlparse

from .canonicalizers import basic_clean


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None

    value = basic_clean(phone)
    if not value:
        return None

    value = re.sub(r"[^\d+()/\-\s]", "", value)
    value = re.sub(r"\s+", " ", value).strip()

    return value or None


def normalize_email(email: Optional[str]) -> Optional[str]:
    if not email:
        return None

    value = basic_clean(email)
    if not value:
        return None

    value = value.lower()

    return value or None


def normalize_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None

    value = basic_clean(url)
    if not value:
        return None

    if value.startswith("//"):
        value = "https:" + value

    if not re.match(r"^https?://", value, flags=re.IGNORECASE):
        value = "https://" + value

    return value


def extract_domain(url: Optional[str]) -> Optional[str]:
    if not url:
        return None

    normalized = normalize_url(url)
    if not normalized:
        return None

    try:
        parsed = urlparse(normalized)
        domain = parsed.netloc.lower().strip()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain or None

    except Exception:
        return None