import argparse
import json
from pathlib import Path
from typing import Any


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    rows = load_json(input_path)

    for row in rows:
        row["batch_status"] = "passed"

    save_json(output_path, rows)

    print("\nBATCH STATUS APLICADO\n")
    print(f"records: {len(rows)}")
    print(f"output: {output_path}")


if __name__ == "__main__":
    main()