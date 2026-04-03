from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.catalogo.scraping.versiones.v3.runner import run_scraper


def main() -> None:
    output_dir = ROOT / "data/samples/output/versiones_scraper_v3"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    html_dir = ROOT / "data/samples/input/html_examples"
    html_files = sorted(str(path) for path in html_dir.glob("*.txt"))
    run_scraper(
        csv_path=None,
        contract_path=ROOT / "contracts/catalogo/t_versiones.contract.json",
        output_dir=output_dir,
        html_files=html_files,
    )
    print("Smoke test completado")


if __name__ == "__main__":
    main()
