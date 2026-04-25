import json
from pathlib import Path
from typing import List

from ..models.concesionario_raw_record import ConcesionarioRawRecord


class StagingLoader:

    @staticmethod
    def load_json(path: str) -> List[ConcesionarioRawRecord]:
        p = Path(path)

        if not p.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")

        data = json.loads(p.read_text(encoding="utf-8"))

        if "records" not in data:
            raise ValueError("El JSON no contiene 'records'")

        records = []

        for i, item in enumerate(data["records"]):
            try:
                record = ConcesionarioRawRecord(
                    record_external_id=item.get("record_external_id", ""),

                    dealer_name_raw=item.get("dealer_name_raw", ""),
                    dealer_type_raw=item.get("dealer_type_raw"),

                    address_raw=item.get("address_raw"),
                    location_raw=item.get("location_raw", ""),
                    postal_code_raw=item.get("postal_code_raw"),

                    phone_raw=item.get("phone_raw"),
                    email_raw=item.get("email_raw"),
                    website_raw=item.get("website_raw"),

                    instagram_raw=item.get("instagram_raw"),
                    facebook_raw=item.get("facebook_raw"),
                    tiktok_raw=item.get("tiktok_raw"),
                    youtube_raw=item.get("youtube_raw"),
                    google_business_profile_raw=item.get("google_business_profile_raw"),

                    brands_raw=item.get("brands_raw"),
                    description_raw=item.get("description_raw"),

                    source_name=item.get("_merged_source_name", data.get("source_name", "")),
                    source_url=item.get("_merged_source_url", data.get("source_url", "")),
                    source_row_url=item.get("source_row_url", ""),

                    scrape_date=item.get("_merged_scrape_date", data.get("scrape_date", "")),

                    raw_payload=item
                )

                records.append(record)

            except Exception as e:
                print(f"[STAGING ERROR] fila {i}: {e}")

        return records