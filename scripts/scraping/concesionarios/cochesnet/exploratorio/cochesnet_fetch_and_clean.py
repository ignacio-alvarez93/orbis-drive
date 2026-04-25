from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from seleniumbase import sb_cdp


REMOVE_TAGS = ["script", "style", "noscript", "svg"]


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag_name in REMOVE_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()
    return soup.prettify()


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Descarga HTML con SeleniumBase CDP y genera una copia limpia con BeautifulSoup."
    )
    parser.add_argument("url", help="URL a visitar")
    parser.add_argument(
        "--output-dir",
        default="data/external/concesionarios/cochesnet",
        help="Directorio base de salida",
    )
    parser.add_argument("--wait", type=float, default=5.0, help="Espera tras la carga")
    parser.add_argument(
        "--disconnect-before-source",
        action="store_true",
        help="Prueba a hacer disconnect/connect antes de leer el HTML",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecuta el navegador en headless si el entorno lo permite",
    )
    args = parser.parse_args()

    base_dir = Path(args.output_dir)
    raw_dir = base_dir / "html"
    clean_dir = base_dir / "cleaned"
    logs_dir = base_dir / "logs"
    snapshots_dir = base_dir / "snapshots"
    for d in [raw_dir, clean_dir, logs_dir, snapshots_dir]:
        d.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = raw_dir / f"cochesnet_{ts}.html"
    clean_path = clean_dir / f"cochesnet_{ts}_clean.html"
    snapshot_path = snapshots_dir / f"cochesnet_{ts}_unexpected.html"
    log_path = logs_dir / "run_log.jsonl"

    browser_kwargs = {
        "headed": not args.headless,
    }

    sb = sb_cdp.Chrome(**browser_kwargs)
    status = "ok"
    error_message = None

    try:
        sb.get(args.url)
        sb.sleep(args.wait)

        if args.disconnect_before_source:
            try:
                sb.disconnect()
                sb.sleep(1.0)
                sb.connect()
                sb.sleep(1.0)
            except Exception as reconnect_error:
                append_jsonl(
                    log_path,
                    {
                        "timestamp": ts,
                        "url": args.url,
                        "event": "disconnect_connect_failed",
                        "error": repr(reconnect_error),
                    },
                )

        html = sb.get_page_source()
        raw_path.write_text(html, encoding="utf-8")

        cleaned = clean_html(html)
        clean_path.write_text(cleaned, encoding="utf-8")

        body_text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
        if "captcha" in body_text.lower() or "access denied" in body_text.lower():
            snapshot_path.write_text(html, encoding="utf-8")
            status = "warning"
            error_message = "possible_challenge_detected"

    except Exception as exc:
        status = "error"
        error_message = repr(exc)
        try:
            html = sb.get_page_source()
            snapshot_path.write_text(html, encoding="utf-8")
        except Exception:
            pass
    finally:
        append_jsonl(
            log_path,
            {
                "timestamp": ts,
                "url": args.url,
                "status": status,
                "raw_html_path": str(raw_path),
                "clean_html_path": str(clean_path),
                "snapshot_path": str(snapshot_path) if snapshot_path.exists() else None,
                "error": error_message,
            },
        )
        try:
            sb.driver.stop()
        except Exception:
            pass

    print(f"Estado: {status}")
    print(f"HTML bruto: {raw_path}")
    print(f"HTML limpio: {clean_path}")
    if snapshot_path.exists():
        print(f"Snapshot: {snapshot_path}")
    print(f"Log: {log_path}")


if __name__ == "__main__":
    main()
