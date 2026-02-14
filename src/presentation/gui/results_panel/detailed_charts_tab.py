#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Detailed Charts Tab Module
📈 "Részletes Diagramok" TAB - Nagy, professzionális chartok
🔧 KRITIKUS JAVÍTÁS: WindChart integráció - HIÁNYZÓ CHART FRISSÍTÉS
🌪️ WIND CHART INTEGRÁCIÓ: WindChart és WindRoseChart explicit frissítése
"""

import logging
from typing import Any, Dict, Optional

from PySide6.QtWidgets import QVBoxLayout, QWidget

from src.presentation.gui.theme_manager import (
    get_theme_manager,
    register_widget_for_theming,
)

from ..chart_container import ChartsContainer

# Logging konfigurálása
logger = logging.getLogger(__name__)


class DetailedChartsTab(QWidget):
    """
    📈 "Részletes Diagramok" TAB - Nagy, professzionális chartok.
    🔧 KRITIKUS JAVÍTÁS: WindChart integráció - HIÁNYZÓ CHART FRISSÍTÉS
    🌪️ WIND CHART INTEGRÁCIÓ: WindChart és WindRoseChart explicit frissítése
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        logger.debug("DetailedChartsTab inicializálás START")

        # === THEMEMANAGER INICIALIZÁLÁSA ===
        self.theme_manager = get_theme_manager()

        self.charts_container: Optional[ChartsContainer] = None

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

    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🔧 KRITIKUS JAVÍTÁS: Részletes chartok frissítése - WIND CHART INTEGRÁCIÓ.

        Args:
            data: OpenMeteo API válasz
        """
        logger.info(
            "🌪️ KRITIKUS JAVÍTÁS: DetailedChartsTab.update_data() - WIND CHART INTEGRÁCIÓ!"
        )

        # === CHARTS CONTAINER ELLENŐRZÉS ===
        if self.charts_container:
            logger.debug("charts_container EXISTS - calling update_charts...")

            try:
                # 🌪️ KRITIKUS JAVÍTÁS: Explicit chart frissítés logging
                logger.info(
                    "🌪️ WIND CHART DEBUG: Calling charts_container.update_charts() with data..."
                )

                self.charts_container.update_charts(data)

                # 🌪️ EXPLICIT WIND CHART ELLENŐRZÉS
                if hasattr(self.charts_container, "wind_chart"):
                    logger.info("🌪️ WIND CHART DEBUG: wind_chart EXISTS in container!")
                    if hasattr(self.charts_container.wind_chart, "current_data"):
                        wind_data = self.charts_container.wind_chart.current_data
                        if wind_data is not None:
                            logger.info(
                                f"🌪️ WIND CHART SUCCESS: Wind chart has data: {len(wind_data) if hasattr(wind_data, '__len__') else 'non-empty'}"
                            )
                        else:
                            logger.warning(
                                "🌪️ WIND CHART WARNING: Wind chart current_data is None!"
                            )
                    else:
                        logger.warning(
                            "🌪️ WIND CHART WARNING: Wind chart has no current_data attribute!"
                        )
                else:
                    logger.error(
                        "🌪️ WIND CHART ERROR: wind_chart NOT FOUND in container!"
                    )

                # 🌹 EXPLICIT WIND ROSE CHART ELLENŐRZÉS
                if hasattr(self.charts_container, "windrose_chart"):
                    logger.info(
                        "🌹 WIND ROSE DEBUG: windrose_chart EXISTS in container!"
                    )
                    if hasattr(self.charts_container.windrose_chart, "current_data"):
                        windrose_data = (
                            self.charts_container.windrose_chart.current_data
                        )
                        if windrose_data is not None:
                            logger.info(
                                f"🌹 WIND ROSE SUCCESS: Wind rose chart has data: {len(windrose_data) if hasattr(windrose_data, '__len__') else 'non-empty'}"
                            )
                        else:
                            logger.warning(
                                "🌹 WIND ROSE WARNING: Wind rose chart current_data is None!"
                            )
                    else:
                        logger.warning(
                            "🌹 WIND ROSE WARNING: Wind rose chart has no current_data attribute!"
                        )
                else:
                    logger.error(
                        "🌹 WIND ROSE ERROR: windrose_chart NOT FOUND in container!"
                    )

                logger.info(
                    "✅ DetailedChartsTab: charts_container.update_charts() SIKERES! (WIND CHART INTEGRATION)"
                )

            except Exception as e:
                logger.error(
                    f"❌ HIBA a charts_container.update_charts() hívásban: {e}"
                )
                logger.error(f"❌ Exception type: {type(e).__name__}")
                import traceback

                logger.error(f"❌ Traceback: {traceback.format_exc()}")
        else:
            logger.error("❌ charts_container is None! - Ez a probléma oka!")

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
