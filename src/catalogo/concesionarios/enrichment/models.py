from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..models.concesionario_resolved import ConcesionarioResolved


@dataclass
class EnrichmentPayload:
    resolved: ConcesionarioResolved

    telefono: Optional[str]
    email: Optional[str]
    website_url: Optional[str]
    website_domain: Optional[str]

    instagram_profile_url: Optional[str]
    facebook_page_url: Optional[str]
    tiktok_profile_url: Optional[str]
    youtube_channel_url: Optional[str]
    google_business_profile_url: Optional[str]

    direccion_texto: Optional[str]
    codigo_postal: Optional[str]
    ubicacion_raw: Optional[str]

    description_raw: Optional[str]
    brands_raw: Optional[List[str]]

    flags: Dict[str, Any] = field(default_factory=dict)
    derived: Dict[str, Any] = field(default_factory=dict)