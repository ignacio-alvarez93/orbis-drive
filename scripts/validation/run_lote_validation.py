from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from src.catalogo.validacion_lote.lote_catalogo import LoteCatalogo


def main() -> int:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/data/lote_t_versiones.json")
    result = LoteCatalogo().validate_file(input_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
