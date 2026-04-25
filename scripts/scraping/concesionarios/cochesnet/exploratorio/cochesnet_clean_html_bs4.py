from __future__ import annotations

import argparse
from pathlib import Path

from bs4 import BeautifulSoup


REMOVE_TAGS = ["script", "style", "noscript", "svg"]


def clean_html(html: str, prettify: bool = True) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag_name in REMOVE_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    for tag in soup.find_all(True):
        attrs_to_remove = []
        for attr in list(tag.attrs.keys()):
            if attr.startswith("data-") or attr in {"style", "onclick", "onload"}:
                attrs_to_remove.append(attr)
        for attr in attrs_to_remove:
            tag.attrs.pop(attr, None)

    return soup.prettify() if prettify else str(soup)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Limpia un HTML con BeautifulSoup y guarda una versión legible."
    )
    parser.add_argument("input_html", help="Ruta al HTML de entrada")
    parser.add_argument(
        "--output-html",
        help="Ruta del HTML limpio de salida. Si no se indica, se genera junto al original.",
    )
    parser.add_argument(
        "--no-prettify",
        action="store_true",
        help="No reformatea el HTML",
    )
    args = parser.parse_args()

    input_path = Path(args.input_html)
    output_path = (
        Path(args.output_html)
        if args.output_html
        else input_path.with_name(f"{input_path.stem}_clean.html")
    )

    html = input_path.read_text(encoding="utf-8")
    cleaned = clean_html(html, prettify=not args.no_prettify)
    output_path.write_text(cleaned, encoding="utf-8")
    print(f"HTML limpio guardado en: {output_path}")


if __name__ == "__main__":
    main()
