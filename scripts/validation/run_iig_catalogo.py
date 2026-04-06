import argparse
import json

from src.catalogo.iig.iig_catalogo import IIG_Catalogo


def safe_print(label, value):
    text = f"{label}: {value}"
    print(text.encode("cp1252", errors="replace").decode("cp1252"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--contract", required=True)
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    iig = IIG_Catalogo(contract_path=args.contract)
    result = iig.validate_batch(data)

    print("\nRESULTADO IIG\n")
    safe_print("Tipo", type(result).__name__)

    print("\nDETALLE\n")
    for attr in dir(result):
        if attr.startswith("_"):
            continue
        try:
            value = getattr(result, attr)
            if callable(value):
                continue
            safe_print(attr, value)
        except Exception as e:
            safe_print(attr, f"<error leyendo atributo: {e}>")

if __name__ == "__main__":
    main()