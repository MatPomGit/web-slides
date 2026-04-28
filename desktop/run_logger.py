"""Narzędzia do konfiguracji logowania uruchomień aplikacji."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path


def _build_run_log_path(log_dir: str) -> Path:
    """Tworzy ścieżkę pliku logu unikalną dla pojedynczego uruchomienia."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(log_dir) / f"run_{timestamp}.log"


def configure_run_logging(log_level: str, log_dir: str) -> Path:
    """Konfiguruje logowanie do konsoli i pliku dla bieżącego uruchomienia.

    Funkcja tworzy katalog na logi, ustawia wspólny formatter oraz podłącza dwa
    handlery: konsolowy i plikowy. Dzięki temu każde uruchomienie aplikacji ma
    osobny plik logu, który można później analizować.
    """
    run_log_path = _build_run_log_path(log_dir)
    run_log_path.parent.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.FileHandler(run_log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    logging.info("Zainicjalizowano logowanie uruchomienia. Plik logu: %s", run_log_path)
    return run_log_path
