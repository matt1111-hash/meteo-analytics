# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from analytics_tabs.py."""

from __future__ import annotations

from .analytics_tabs_part1 import (
    PrecipitationTabWidget,
    TemperatureTabWidget,
    WindTabWidget,
)
from .analytics_tabs_part2 import WindGustTabWidget
from .analytics_tabs_support import *


class ClimateTabWidget(QTabWidget):
    """🌡️ Klímakutató tab widget - 4 KONSTANS HEATMAP TAB + 2 DEDICATED WIND CHART - BEAUFORT + MAX SZÉLLÖKÉS VERZIÓ"""

    def __init__(self):  # noqa: D107
        super().__init__()

        # Tab widget-ek létrehozása - KONSTANS HEATMAP VERZIÓK
        self.temp_tab = TemperatureTabWidget()  # 🌡️ Hőmérséklet KONSTANS HEATMAP
        self.precip_tab = PrecipitationTabWidget()  # 🌧️ Csapadék KONSTANS HEATMAP
        self.wind_tab = WindTabWidget()  # 💨 Szél KONSTANS HEATMAP (BEAUFORT, átlagos max)
        self.windgust_tab = (
            WindGustTabWidget()
        )  # 🌪️ Max Széllökés KONSTANS HEATMAP (BEAUFORT, gusts)

        # 🌪️ DEDICATED WIND CHARTOK HOZZÁADÁSA
        self.dedicated_wind_chart = WindChart()  # 🌪️ WindChart dedicated
        self.dedicated_windrose_chart = WindRoseChart()  # 🌹 WindRoseChart dedicated

        self._setup_tabs()

        # Lazy loading tracking
        self.data_cache = None
        self.tabs_initialized = {
            "temp": False,
            "precip": False,
            "wind": False,
            "windgust": False,
            "wind_chart": False,
            "windrose_chart": False,
        }

        # Tab változás figyelése
        self.currentChanged.connect(self._on_tab_changed)

        logger.info(
            "ClimateTabWidget inicializálva - 4 KONSTANS HEATMAP TAB + 2 DEDICATED WIND CHART (365 téglalap, BEAUFORT szél + max széllökés)"
        )

    def _setup_tabs(self):
        """Tab-ok beállítása - KONSTANS HEATMAP-EK + MAX SZÉLLÖKÉS + DEDICATED WIND CHARTOK"""
        # Tab-ok hozzáadása
        self.addTab(self.temp_tab, "🌡️ Hőmérséklet")  # KONSTANS HEATMAP
        self.addTab(self.precip_tab, "🌧️ Csapadék")  # KONSTANS HEATMAP (0mm=fehér)
        self.addTab(self.wind_tab, "💨 Szél")  # KONSTANS HEATMAP (BEAUFORT, átlagos max)
        self.addTab(self.windgust_tab, "🌪️ Max Széllökés")  # KONSTANS HEATMAP (BEAUFORT, max gusts)

        # 🌪️ DEDICATED WIND CHARTOK HOZZÁADÁSA
        self.addTab(self.dedicated_wind_chart, "🌪️ Széllökések")  # DEDICATED WindChart
        self.addTab(self.dedicated_windrose_chart, "🌹 Széllökés Rózsa")  # DEDICATED WindRoseChart

        # Tab styling
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f9fafb;
                border: 1px solid #d1d5db;
                border-bottom-color: transparent;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 12px;
                margin-right: 2px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #C43939;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #f3f4f6;
            }
        """)

    def update_data(self, data: Dict[str, Any]):
        """🎯 KONSTANS HEATMAP + DEDICATED WIND CHARTOK Tab widget adatok frissítése - BEAUFORT + MAX SZÉLLÖKÉS VERZIÓ"""
        try:
            # Adatok cache-elése
            self.data_cache = data

            # Aktív tab frissítése
            current_index = self.currentIndex()
            self._update_current_tab(current_index)

            # 🌪️ KRITIKUS JAVÍTÁS: DEDICATED WIND CHARTOK MINDIG FRISSÍTÉSE
            logger.debug("DEDICATED WIND CHARTOK frissítése...")

            try:
                self.dedicated_wind_chart.update_data(data)
                logger.debug("dedicated_wind_chart frissítve!")
            except Exception as e:
                logger.error(f"dedicated_wind_chart hiba: {e}")

            try:
                self.dedicated_windrose_chart.update_data(data)
                logger.debug("dedicated_windrose_chart frissítve!")
            except Exception as e:
                logger.error(f"dedicated_windrose_chart hiba: {e}")

            # Teljes napok számának logolása
            daily_data = data.get("daily", {})
            dates = daily_data.get("time", [])
            total_days = len(dates)

            logger.info(
                f"🎯 ClimateTabWidget frissítve - {total_days} nap → 365 téglalap/tab (BEAUFORT szél + max széllökés)"
            )

        except Exception as e:
            logger.error(f"ClimateTabWidget frissítési hiba: {e}")

    def _on_tab_changed(self, index: int):
        """Tab váltás kezelője - lazy loading"""
        logger.info(f"Tab váltás: {index}")
        self._update_current_tab(index)

    def _update_current_tab(self, index: int):
        """Aktív tab frissítése - KONSTANS HEATMAP VERZIÓK + MAX SZÉLLÖKÉS + DEDICATED WIND CHARTOK"""
        if not self.data_cache:
            return

        try:
            if index == 0:  # Hőmérséklet tab (konstans heatmap)
                self.temp_tab.update_data(self.data_cache)
                self.tabs_initialized["temp"] = True
            elif index == 1:  # Csapadék tab (konstans heatmap, 0mm=fehér)
                self.precip_tab.update_data(self.data_cache)
                self.tabs_initialized["precip"] = True
            elif index == 2:  # Szél tab (konstans heatmap, BEAUFORT, átlagos max)  # noqa: PLR2004
                self.wind_tab.update_data(self.data_cache)
                self.tabs_initialized["wind"] = True
            elif (
                index == 3  # noqa: PLR2004
            ):  # Max Széllökés tab (konstans heatmap, BEAUFORT, max gusts)
                self.windgust_tab.update_data(self.data_cache)
                self.tabs_initialized["windgust"] = True
            elif index == 4:  # 🌪️ DEDICATED WindChart tab  # noqa: PLR2004
                self.dedicated_wind_chart.update_data(self.data_cache)
                self.tabs_initialized["wind_chart"] = True
                logger.debug("DEDICATED WindChart tab aktívált és frissítve!")
            elif index == 5:  # 🌹 DEDICATED WindRoseChart tab  # noqa: PLR2004
                self.dedicated_windrose_chart.update_data(self.data_cache)
                self.tabs_initialized["windrose_chart"] = True
                logger.debug("DEDICATED WindRoseChart tab aktívált és frissítve!")

        except Exception as e:
            logger.error(f"Tab {index} frissítési hiba: {e}")
