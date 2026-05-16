#!/usr/bin/env python3
# mypy: ignore-errors

"""
Global Weather Analyzer - Detailed Charts Tab Module
📈 "Részletes Diagramok" TAB - Nagy, professzionális chartok
🔧 KRITIKUS JAVÍTÁS: WindChart integráció - HIÁNYZÓ CHART FRISSÍTÉS
🌪️ WIND CHART INTEGRÁCIÓ: WindChart és WindRoseChart explicit frissítése
"""

import logging
from typing import Any

from PySide6.QtWidgets import QVBoxLayout, QWidget

from src.presentation.gui.theme_manager import (
    get_theme_manager,
    register_widget_for_theming,
)

from ..chart_container import ChartsContainer

# Logging konfigurálása
logger = logging.getLogger(__name__)


def _describe_chart_data(chart: Any) -> str:
    """Return a readable chart data status."""
    if not hasattr(chart, "current_data"):
        return "no current_data attribute"
    chart_data = chart.current_data
    if chart_data is None:
        return "current_data is None"
    if hasattr(chart_data, "__len__"):
        return f"data length={len(chart_data)}"
    return "non-empty data"


class DetailedChartsTab(QWidget):
    """
    📈 "Részletes Diagramok" TAB - Nagy, professzionális chartok.
    🔧 KRITIKUS JAVÍTÁS: WindChart integráció - HIÁNYZÓ CHART FRISSÍTÉS
    🌪️ WIND CHART INTEGRÁCIÓ: WindChart és WindRoseChart explicit frissítése
    """

    def __init__(self, parent: QWidget | None = None):  # noqa: D107
        super().__init__(parent)

        logger.debug("DetailedChartsTab inicializálás START")

        # === THEMEMANAGER INICIALIZÁLÁSA ===
        self.theme_manager = get_theme_manager()

        self.charts_container: ChartsContainer | None = None

        # UI inicializálása
        self._init_ui()

        # === THEMEMANAGER REGISZTRÁCIÓ ===
        self._register_widgets_for_theming()

        logger.debug("DetailedChartsTab inicializálás BEFEJEZVE")

    def _init_ui(self) -> None:
        """UI inicializálása - nagy chartok."""
        logger.debug("DetailedChartsTab._init_ui() START")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Charts container
        logger.debug("ChartsContainer létrehozása...")
        self.charts_container = ChartsContainer()

        if self.charts_container:
            logger.debug("ChartsContainer sikeresen létrehozva!")
            layout.addWidget(self.charts_container)
        else:
            logger.error("ChartsContainer létrehozása SIKERTELEN!")

        logger.debug("DetailedChartsTab._init_ui() BEFEJEZVE")

    def _register_widgets_for_theming(self) -> None:
        """Widget-ek regisztrálása ThemeManager-hez."""
        register_widget_for_theming(self, "container")
        logger.debug("DetailedChartsTab - Widget regisztrálva ColorPalette API-hez")

    def update_data(self, data: dict[str, Any]) -> None:
        """
        🔧 KRITIKUS JAVÍTÁS: Részletes chartok frissítése - WIND CHART INTEGRÁCIÓ.

        Args:
            data: OpenMeteo API válasz
        """
        logger.info("🌪️ KRITIKUS JAVÍTÁS: DetailedChartsTab.update_data() - WIND CHART INTEGRÁCIÓ!")
        if self.charts_container is None:
            logger.error("❌ charts_container is None! - Ez a probléma oka!")
            return

        logger.debug("charts_container EXISTS - calling update_charts...")
        try:
            logger.info("🌪️ WIND CHART DEBUG: Calling charts_container.update_charts() with data...")
            self.charts_container.update_charts(data)
            self._log_chart_state("wind_chart", "🌪️ WIND CHART")
            self._log_chart_state("windrose_chart", "🌹 WIND ROSE")
            logger.info(
                "✅ DetailedChartsTab: charts_container.update_charts() SIKERES! (WIND CHART INTEGRATION)"
            )
        except Exception as e:
            logger.error(f"❌ HIBA a charts_container.update_charts() hívásban: {e}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            import traceback  # noqa: PLC0415

            logger.error(f"❌ Traceback: {traceback.format_exc()}")

    def clear_data(self) -> None:
        """Chartok törlése."""
        logger.debug("DetailedChartsTab.clear_data() MEGHÍVVA")

        if self.charts_container:
            logger.debug("charts_container létezik - clear_charts() hívása...")
            self.charts_container.clear_charts()
            logger.debug("clear_charts() BEFEJEZVE")
        else:
            logger.error("charts_container is None - nem lehet törölni!")

    def apply_theme(self, dark_theme: bool) -> None:
        """Téma alkalmazása."""
        logger.debug(f"DetailedChartsTab.apply_theme({dark_theme}) MEGHÍVVA")

        if self.charts_container:
            logger.debug("charts_container létezik - apply_theme() hívása...")
            self.charts_container.apply_theme(dark_theme)
            logger.debug("apply_theme() BEFEJEZVE")
        else:
            logger.error("charts_container is None - nem lehet témát alkalmazni!")

    def _log_chart_state(self, attribute_name: str, label: str) -> None:
        """Log state for a chart embedded in the container."""
        if self.charts_container is None or not hasattr(self.charts_container, attribute_name):
            logger.error(f"{label} ERROR: {attribute_name} NOT FOUND in container!")
            return
        chart = getattr(self.charts_container, attribute_name)
        logger.info(f"{label} DEBUG: {attribute_name} EXISTS in container!")
        status = _describe_chart_data(chart)
        if status in {"current_data is None", "no current_data attribute"}:
            logger.warning(f"{label} WARNING: {status}!")
        else:
            logger.info(f"{label} SUCCESS: {status}")
