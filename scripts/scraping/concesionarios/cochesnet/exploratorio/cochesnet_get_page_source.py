from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from seleniumbase import sb_cdp


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Descarga el page source de una URL usando SeleniumBase CDP."
    )
    parser.add_argument("url", help="URL a visitar")
    parser.add_argument(
        "--output-dir",
        default="data/external/concesionarios/cochesnet/html",
        help="Directorio de salida",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=4.0,
        help="Espera adicional tras cargar la página",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecuta el navegador en headless si el entorno lo permite",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = output_dir / f"page_source_{ts}.html"

    browser_kwargs = {
        "headed": not args.headless,
    }

    sb = sb_cdp.Chrome(**browser_kwargs)
    try:
        sb.get(args.url)
        sb.sleep(args.timeout)
        html = sb.get_page_source()
        html_path.write_text(html, encoding="utf-8")
        print(f"HTML guardado en: {html_path}")
    finally:
        try:
            sb.driver.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
