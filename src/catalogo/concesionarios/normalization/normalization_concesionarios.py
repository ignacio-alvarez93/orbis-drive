from typing import List

from ..models.concesionario_raw_record import ConcesionarioRawRecord
from ..models.concesionario_normalized import ConcesionarioNormalized
from .canonicalizers import (
    basic_clean,
    canonicalize_name,
    normalize_address,
    normalize_postal_code,
)
from .contact_utils import (
    normalize_email,
    normalize_phone,
    normalize_url,
    extract_domain,
)
from .location_prep import build_location_candidates


TIPO_MAP = {
    "oficial": "oficial",
    "concesionario oficial": "oficial",
    "compraventa": "compraventa",
    "multimarca": "multimarca",
    "taller_comercial": "taller_comercial",
    "red_comercial": "red_comercial",
    "otro": "otro",
}


def normalize_dealer_type(value: str | None) -> str | None:
    cleaned = basic_clean(value)
    if not cleaned:
        return None

    lowered = cleaned.lower()
    return TIPO_MAP.get(lowered, lowered)


class NormalizationConcesionarios:

    @classmethod
    def normalize_record(cls, record: ConcesionarioRawRecord) -> ConcesionarioNormalized:
        record.dealer_name_raw = basic_clean(record.dealer_name_raw) or ""
        record.dealer_type_raw = basic_clean(record.dealer_type_raw)

        record.address_raw = normalize_address(record.address_raw)
        record.location_raw = basic_clean(record.location_raw) or ""
        record.postal_code_raw = normalize_postal_code(record.postal_code_raw)

        record.phone_raw = normalize_phone(record.phone_raw)
        record.email_raw = normalize_email(record.email_raw)
        record.website_raw = normalize_url(record.website_raw)

        record.instagram_raw = normalize_url(record.instagram_raw)
        record.facebook_raw = normalize_url(record.facebook_raw)
        record.tiktok_raw = normalize_url(record.tiktok_raw)
        record.youtube_raw = normalize_url(record.youtube_raw)
        record.google_business_profile_raw = normalize_url(record.google_business_profile_raw)

        record.description_raw = basic_clean(record.description_raw)

        if record.brands_raw is not None:
            record.brands_raw = [
                b for b in (basic_clean(x) for x in record.brands_raw) if b
            ]

        nombre_canonical = canonicalize_name(record.dealer_name_raw)
        direccion_texto_normalizada = normalize_address(record.address_raw)
        codigo_postal_normalizado = normalize_postal_code(record.postal_code_raw)
        website_domain = extract_domain(record.website_raw)
        tipo_concesionario_normalizado = normalize_dealer_type(record.dealer_type_raw)

        location_candidates = build_location_candidates(
            address_raw=record.address_raw,
            postal_code_raw=record.postal_code_raw,
            location_raw=record.location_raw,
        )

        return ConcesionarioNormalized(
            raw=record,
            nombre_canonical=nombre_canonical,
            direccion_texto_normalizada=direccion_texto_normalizada,
            codigo_postal_normalizado=codigo_postal_normalizado,
            website_domain=website_domain,
            tipo_concesionario_normalizado=tipo_concesionario_normalizado,
            location_candidates=location_candidates,
        )

    @classmethod
    def batch_normalize(cls, records: List[ConcesionarioRawRecord]) -> List[ConcesionarioNormalized]:
        return [cls.normalize_record(record) for record in records]