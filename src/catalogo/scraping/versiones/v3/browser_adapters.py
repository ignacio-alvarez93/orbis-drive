from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BrowserConfig:
    headless: bool = False
    uc: bool = True


class BrowserAdapter:
    """
    Adaptador mínimo para navegación visible con SeleniumBase.
    Preferencia:
    1. sb_cdp.Chrome(...)
    2. SB(...).activate_cdp_mode(...)
    """

    def __init__(self, config: BrowserConfig | None = None) -> None:
        self.config = config or BrowserConfig()
        self._driver = None
        self._sb = None
        self._mode = None

    def open(self, url: str) -> None:
        if self._driver is None and self._sb is None:
            self._bootstrap()

        if self._mode == "cdp_driver":
            self._driver.get(url)
            return

        if self._mode == "sb_cdp":
            self._sb.activate_cdp_mode(url)
            return

        raise RuntimeError("No hay navegador inicializado")

    def get_page_source(self) -> str:
        if self._mode == "cdp_driver":
            return self._driver.get_page_source()
        if self._mode == "sb_cdp":
            return self._sb.get_page_source()
        raise RuntimeError("No hay navegador inicializado")

    def close(self) -> None:
        try:
            if self._mode == "cdp_driver" and self._driver is not None:
                quit_method = getattr(self._driver, "quit", None)
                if callable(quit_method):
                    quit_method()
            elif self._mode == "sb_cdp" and self._sb is not None:
                quit_method = getattr(self._sb, "quit", None)
                if callable(quit_method):
                    quit_method()
        finally:
            self._driver = None
            self._sb = None
            self._mode = None

    def _bootstrap(self) -> None:
        # Opción preferente: sb_cdp.Chrome(...)
        try:
            from seleniumbase import sb_cdp  # type: ignore

            self._driver = sb_cdp.Chrome(
                uc=self.config.uc,
                headed=not self.config.headless,
            )
            self._mode = "cdp_driver"
            return
        except Exception:
            pass

        # Fallback: SB(...).activate_cdp_mode(...)
        try:
            from seleniumbase import SB  # type: ignore

            self._sb = SB(
                uc=self.config.uc,
                test=False,
                headless=self.config.headless,
            )
            self._sb.__enter__()
            self._mode = "sb_cdp"
            return
        except Exception as exc:
            raise RuntimeError(
                "No se pudo inicializar SeleniumBase ni en modo sb_cdp.Chrome "
                "ni en modo SB(...).activate_cdp_mode(...)."
            ) from exc


def build_browser() -> BrowserAdapter:
    return BrowserAdapter()
