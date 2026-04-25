import re
from typing import List

from ...models.concesionario_normalized import ConcesionarioNormalized


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
URL_RE = re.compile(r"^https?://", flags=re.IGNORECASE)


def validate_contact(normalized: ConcesionarioNormalized) -> List[str]:
    warnings: List[str] = []

    email_value = normalized.raw.email_raw
    website_value = normalized.raw.website_raw
    phone_value = normalized.raw.phone_raw

    if email_value and not EMAIL_RE.match(email_value):
        warnings.append("email_raw con formato no valido")

    if website_value and not URL_RE.match(website_value):
        warnings.append("website_raw con formato no valido")

    if phone_value:
        digits = re.sub(r"\D", "", phone_value)
        if len(digits) < 6:
            warnings.append("phone_raw demasiado corto o poco fiable")

    return warnings