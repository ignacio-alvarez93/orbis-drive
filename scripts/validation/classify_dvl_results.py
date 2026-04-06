import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.catalogo.dvl.dvl_catalogo import DVL_Catalogo


PENDING_REASON_CODES = {
    "critical_field_missing": [
        "campo crítico ausente",
        "campo crítico ausente o inválido",
        "critical field missing",
    ]
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"El archivo {path} no contiene una lista JSON.")
    return data


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def extract_result_payload(result: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {}

    for attr in ("is_valid", "errors", "warnings", "metrics", "normalized_data"):
        if hasattr(result, attr):
            value = getattr(result, attr)
            if attr == "metrics":
                if hasattr(value, "__dict__"):
                    value = value.__dict__
                else:
                    value = str(value)
            payload[attr] = value

    return payload


def normalize_errors(errors: Any) -> list[str]:
    if errors is None:
        return []
    if isinstance(errors, list):
        return [str(e) for e in errors]
    return [str(errors)]


def is_pending_recoverable(errors: list[str]) -> bool:
    lowered = " | ".join(errors).lower()
    for patterns in PENDING_REASON_CODES.values():
        for pattern in patterns:
            if pattern.lower() in lowered:
                return True
    return False


def classify_record(
    row_index: int,
    original_record: dict[str, Any],
    dvl_result: Any,
) -> tuple[str, dict[str, Any]]:
    result_payload = extract_result_payload(dvl_result)
    errors = normalize_errors(result_payload.get("errors"))
    warnings = result_payload.get("warnings", [])
    is_valid = bool(result_payload.get("is_valid"))

    if is_valid:
        enriched = dict(original_record)
        enriched["iig_status"] = "passed"
        enriched["dvl_status"] = "passed"
        return "INGESTABLE", enriched

    classification = (
        "PENDIENTE_RECUPERABLE"
        if is_pending_recoverable(errors)
        else "RECHAZADO_TECNICO"
    )

    reason_code = (
        "critical_field_missing"
        if classification == "PENDIENTE_RECUPERABLE"
        else "technical_rejection"
    )

    envelope = {
        "row_index": row_index,
        "pipeline_stage": "DVL",
        "classification": classification,
        "reason_code": reason_code,
        "reason_detail": "; ".join(errors) if errors else "Sin detalle",
        "detected_at": utc_now_iso(),
        "warnings": warnings,
        "dvl_result": result_payload,
        "record": original_record,
    }
    return classification, envelope


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSON de entrada del lote.")
    parser.add_argument(
        "--valid-output",
        required=True,
        help="Ruta del JSON con registros DVL válidos.",
    )
    parser.add_argument(
        "--pending-output",
        default="data/catalogo_pendientes/pendientes_dvl.json",
        help="Ruta del JSON de pendientes recuperables.",
    )
    parser.add_argument(
        "--rejected-output",
        default="data/catalogo_pendientes/rechazados_tecnicos.json",
        help="Ruta del JSON de rechazados técnicos.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    valid_output = Path(args.valid_output)
    pending_output = Path(args.pending_output)
    rejected_output = Path(args.rejected_output)

    rows = load_json(input_path)
    dvl = DVL_Catalogo()

    valid_rows: list[dict[str, Any]] = []
    pending_rows: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []

    for idx, row in enumerate(rows, start=1):
        try:
            result = dvl.validate(row)
            classification, payload = classify_record(idx, row, result)

            if classification == "INGESTABLE":
                valid_rows.append(payload)
            elif classification == "PENDIENTE_RECUPERABLE":
                pending_rows.append(payload)
            else:
                rejected_rows.append(payload)

        except Exception as exc:
            rejected_rows.append(
                {
                    "row_index": idx,
                    "pipeline_stage": "DVL",
                    "classification": "RECHAZADO_TECNICO",
                    "reason_code": "dvl_exception",
                    "reason_detail": str(exc),
                    "detected_at": utc_now_iso(),
                    "warnings": [],
                    "dvl_result": {},
                    "record": row,
                }
            )

    save_json(valid_output, valid_rows)
    save_json(pending_output, pending_rows)
    save_json(rejected_output, rejected_rows)

    print("\nCLASIFICACION DVL\n")
    print(f"input_records: {len(rows)}")
    print(f"ingestables: {len(valid_rows)}")
    print(f"pendientes_recuperables: {len(pending_rows)}")
    print(f"rechazados_tecnicos: {len(rejected_rows)}")
    print(f"valid_output: {valid_output}")
    print(f"pending_output: {pending_output}")
    print(f"rejected_output: {rejected_output}")


if __name__ == "__main__":
    main()