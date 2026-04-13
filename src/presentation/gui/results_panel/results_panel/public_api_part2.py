# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from public_api.py."""

from __future__ import annotations

from .public_api_support import *


def clear_data(self) -> None:
    """Adatok törlése."""
    logger.debug("ResultsPanel.clear_data() MEGHÍVVA")

    # Loading elrejtése
    if self.is_loading():
        self.hide_loading_indicator()

    # Állapot törlése
    self.current_data = None
    self.current_city = None

    # Title reset
    self.title_label.setText("📊 Időjárási Adatok Elemzése")

    # Tabok törlése
    self.tab_manager.clear_all_tabs()

    logger.debug("ResultsPanel.clear_data() BEFEJEZVE")


# === EXTREME WEATHER ===


def trigger_extreme_weather_analysis(self) -> None:
    """Programmatic extreme weather trigger."""
    logger.info("🔥 Programmatic extreme weather analysis triggered")
    self.extreme_weather_requested.emit()


# === PUBLIKUS GETTEREK ===


def get_charts_container(self):
    """Charts container referenciájának lekérdezése."""
    return self.tab_manager.get_charts_container()


def get_data_table(self):
    """Data table referenciájának lekérdezése."""
    return self.tab_manager.get_data_table()


# === TÉMA KEZELÉS ===


def apply_theme(self, dark_theme: bool) -> None:
    """
    Téma alkalmazása.

    Args:
        self: ResultsPanel instance
        dark_theme: Sötét téma engedélyezve
    """
    logger.debug(f"ResultsPanel.apply_theme({dark_theme}) MEGHÍVVA")
    self.tab_manager.apply_theme(dark_theme)
    logger.debug("ResultsPanel.apply_theme() BEFEJEZVE")


def apply_theme_by_name(self, theme_name: str) -> None:
    """Téma alkalmazása név alapján."""
    if self.theme_manager:
        success = self.theme_manager.set_theme(theme_name)
        if success:
            logger.info(f"ResultsPanel téma alkalmazva: {theme_name}")
        else:
            logger.error(f"ResultsPanel téma alkalmazás sikertelen: {theme_name}")


def get_current_theme_name(self) -> str:
    """Jelenlegi téma nevének lekérdezése."""
    if self.theme_manager:
        return self.theme_manager.get_current_theme()
    return "default"
