import re
import unicodedata
from typing import Optional


def collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def strip_control_chars(value: str) -> str:
    return "".join(ch for ch in value if unicodedata.category(ch)[0] != "C")


def basic_clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    value = strip_control_chars(value)
    value = collapse_spaces(value)

    return value or None


def remove_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def canonicalize_name(name: Optional[str]) -> str:
    if not name:
        return ""

    value = basic_clean(name) or ""
    value = value.lower()
    value = remove_accents(value)

    value = re.sub(r"[^\w\s]", " ", value)
    value = collapse_spaces(value)

    return value


def normalize_postal_code(postal_code: Optional[str]) -> Optional[str]:
    if not postal_code:
        return None

    value = basic_clean(postal_code)
    if not value:
        return None

    digits = re.sub(r"\D", "", value)

    if len(digits) == 5:
        return digits

    return value


def normalize_address(address: Optional[str]) -> Optional[str]:
    if not address:
        return None

    value = basic_clean(address)
    if not value:
        return None

    value = re.sub(r"\s*,\s*", ", ", value)
    value = collapse_spaces(value)

    return value