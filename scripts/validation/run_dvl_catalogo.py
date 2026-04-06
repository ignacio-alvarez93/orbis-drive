import argparse
import json

from src.catalogo.dvl.dvl_catalogo import DVL_Catalogo


def safe_print(label, value):
    text = f"{label}: {value}"
    print(text.encode("cp1252", errors="replace").decode("cp1252"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    dvl = DVL_Catalogo()

    print("\nRESULTADO DVL\n")

    passed = 0
    failed = 0
    results = []

    for idx, row in enumerate(data, start=1):
        try:
            result = dvl.validate(row)

            status = None
            for attr in ("is_valid", "valid", "passed", "ok", "success"):
                if hasattr(result, attr):
                    status = getattr(result, attr)
                    break

            if status is None:
                status = True

            results.append((idx, result, status))

            if status:
                passed += 1
            else:
                failed += 1

        except Exception as e:
            results.append((idx, f"EXCEPTION: {e}", False))
            failed += 1

    safe_print("total_records", len(data))
    safe_print("valid_records", passed)
    safe_print("records_with_errors", failed)

    print("\nDETALLE\n")

    for idx, result, status in results:
        safe_print(f"Fila {idx} status", status)

        if isinstance(result, str):
            safe_print(f"Fila {idx} result", result)
            print("-" * 60)
            continue

        for attr in dir(result):
            if attr.startswith("_"):
                continue
            try:
                value = getattr(result, attr)
                if callable(value):
                    continue
                safe_print(f"Fila {idx} {attr}", value)
            except Exception as e:
                safe_print(f"Fila {idx} {attr}", f"<error leyendo atributo: {e}>")

        print("-" * 60)


if __name__ == "__main__":
    main()