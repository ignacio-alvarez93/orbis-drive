from __future__ import annotations

import json
from datetime import date
from pathlib import Path

BASE_DIR = Path("data/external/concesionarios/cochesnet")
DETAIL_RESULTS = BASE_DIR / "detail_results.json"
OUTPUT_JSON = BASE_DIR / "raw_exploratorio_cochesnet.json"


def main() -> None:
    records = json.loads(DETAIL_RESULTS.read_text(encoding="utf-8"))

    output = {
        "source_name": "cochesnet_concesionarios",
        "source_url": "https://www.coches.net/concesionarios",
        "scrape_date": str(date.today()),
        "records": [],
    }

    for row in records:
        output["records"].append({
            "record_external_id": row.get("record_external_id"),

            "dealer_name_raw": row.get("dealer_name_raw"),
            "dealer_type_raw": row.get("dealer_type_raw"),

            "address_raw": row.get("address_raw"),
            "location_raw": row.get("location_raw"),
            "postal_code_raw": row.get("postal_code_raw"),

            "phone_raw": row.get("phone_raw"),
            "email_raw": row.get("email_raw"),
            "website_raw": row.get("website_raw"),

            "instagram_raw": row.get("instagram_raw"),
            "facebook_raw": row.get("facebook_raw"),
            "tiktok_raw": row.get("tiktok_raw"),
            "youtube_raw": row.get("youtube_raw"),
            "google_business_profile_raw": row.get("google_business_profile_raw"),

            "brands_raw": row.get("brands_raw") or [],
            "description_raw": row.get("description_raw"),

            "source_row_url": row.get("source_row_url"),
            "raw_payload": row.get("raw_payload") or {},
        })

    OUTPUT_JSON.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Registros exportados: {len(output['records'])}")
    print(f"Salida: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()