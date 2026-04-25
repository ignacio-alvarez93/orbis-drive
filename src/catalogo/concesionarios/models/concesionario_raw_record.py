from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class ConcesionarioRawRecord:
    record_external_id: str

    dealer_name_raw: str
    dealer_type_raw: Optional[str] = None

    address_raw: Optional[str] = None
    location_raw: str = ""
    postal_code_raw: Optional[str] = None

    phone_raw: Optional[str] = None
    email_raw: Optional[str] = None
    website_raw: Optional[str] = None

    instagram_raw: Optional[str] = None
    facebook_raw: Optional[str] = None
    tiktok_raw: Optional[str] = None
    youtube_raw: Optional[str] = None
    google_business_profile_raw: Optional[str] = None

    brands_raw: Optional[List[str]] = None
    description_raw: Optional[str] = None

    source_name: str = ""
    source_url: str = ""
    source_row_url: str = ""

    scrape_date: str = ""

    raw_payload: Dict[str, Any] = field(default_factory=dict)