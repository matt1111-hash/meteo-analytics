#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Analytics Tabs Module.
Heatmap tab widgetek az analytics view számára.

🌡️ KONSTANS HEATMAP TAB WIDGET-EK:
✅ TemperatureTabWidget - hőmérséklet heatmap
✅ PrecipitationTabWidget - csapadék heatmap (meteorológiai színek)
✅ WindTabWidget - szél heatmap (BEAUFORT 13 fokozat)
✅ WindGustTabWidget - max széllökés heatmap (BEAUFORT 13 fokozat)
✅ ClimateTabWidget - fő tab widget összesítése
"""

import logging
from typing import Dict, Any

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Qt

from .analytics_helpers import MeteorologicalColorMaps

# Chart imports
from ..charts.heatmap_chart import HeatmapCalendarChart
from ..charts.wind_chart import WindChart
from ..charts.wind_rose_chart import WindRoseChart

logger = logging.getLogger(__name__)


class TemperatureTabWidget(QWidget):
    """🌡️ Hőmérséklet tab - KONSTANS HEATMAP (RdYlBu_r)"""

    def __init__(self):
        super().__init__()

        # HEATMAP CHART
        self.temp_heatmap = HeatmapCalendarChart()
        self.temp_heatmap.figure.set_size_inches(20, 10)  # EXTRA NAGY MÉRET
        self.temp_heatmap.parameter = "temperature_2m_mean"
        self.temp_heatmap.chart_title = "🌡️ Konstans Hőmérséklet Heatmap"

        self._setup_ui()
        logger.info("TemperatureTabWidget inicializálva - KONSTANS HEATMAP (365 téglalap)")

    def _setup_ui(self):
        """Hőmérséklet konstans heatmap tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Heatmap beágyazása
        layout.addWidget(self.temp_heatmap)

    def update_data(self, data: Dict[str, Any]):
        """🎯 Hőmérséklet konstans heatmap frissítés"""
        try:
            # ✅ DIREKT ADATÁTADÁS - aggregáció a heatmap chart-ban történik
            self.temp_heatmap.update_data(data)

            logger.info("🌡️ Hőmérséklet KONSTANS HEATMAP tab frissítve")

        except Exception as e:
            logger.error(f"TemperatureTabWidget KONSTANS HEATMAP frissítési hiba: {e}")


class PrecipitationTabWidget(QWidget):
    """🌧️ Csapadék tab - KONSTANS HEATMAP (meteorológiai színskála)"""

    def __init__(self):
        super().__init__()

        # HEATMAP CHART - CSAPADÉK VERZIÓ
        self.precip_heatmap = HeatmapCalendarChart()
        self.precip_heatmap.figure.set_size_inches(20, 10)  # EXTRA NAGY MÉRET
        self.precip_heatmap.parameter = "precipitation_sum"
        self.precip_heatmap.chart_title = "🌧️ Konstans Csapadék Heatmap"

        # 🎨 METEOROLÓGIAI CSAPADÉK SZÍNSKÁLA
        self.precip_cmap, self.precip_norm = MeteorologicalColorMaps.get_precipitation_colormap()

        self._setup_ui()
        logger.info("PrecipitationTabWidget inicializálva - KONSTANS HEATMAP (365 téglalap, 0mm=fehér)")

    def _setup_ui(self):
        """Csapadék konstans heatmap tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Heatmap beágyazása
        layout.addWidget(self.precip_heatmap)

    def update_data(self, data: Dict[str, Any]):
        """🎯 Csapadék konstans heatmap frissítés - MINDEN TÉGLALAP KITÖLTVE"""
        try:
            # 🎨 METEOROLÓGIAI SZÍNSKÁLA BEÁLLÍTÁSA
            self.precip_heatmap._custom_cmap = self.precip_cmap
            self.precip_heatmap._custom_norm = self.precip_norm
            logger.debug(f"🎨 Csapadék custom colormap beállítva: {type(self.precip_cmap)}")

            # ✅ DIREKT ADATÁTADÁS - aggregáció a heatmap chart-ban történik
            self.precip_heatmap.update_data(data)

            logger.info("🌧️ Csapadék KONSTANS HEATMAP tab frissítve (0mm=fehér)")

        except Exception as e:
            logger.error(f"PrecipitationTabWidget KONSTANS HEATMAP frissítési hiba: {e}")


class WindTabWidget(QWidget):
    """💨 Szél tab - KONSTANS HEATMAP (BEAUFORT-alapú 13 fokozat progresszív színskála) - ÁLGADOS MAX SZÉL"""

    def __init__(self):
        super().__init__()

        # HEATMAP CHART - SZÉL VERZIÓ (ÁLGADOS MAX)
        self.wind_heatmap = HeatmapCalendarChart()
        self.wind_heatmap.figure.set_size_inches(20, 10)  # EXTRA NAGY MÉRET
        self.wind_heatmap.parameter = "windspeed_10m_max"  # ÁLGADOS MAX SZÉL
        self.wind_heatmap.chart_title = "💨 Konstans Szél Heatmap (windspeed_10m_max)"

        # 🎨 BEAUFORT-ALAPÚ 13 FOKOZAT SZÉL SZÍNSKÁLA
        self.wind_cmap, self.wind_norm = MeteorologicalColorMaps.get_wind_colormap()

        self._setup_ui()
        logger.info("WindTabWidget inicializálva - KONSTANS HEATMAP (365 téglalap, BEAUFORT 13 fokozat, átlagos max szél)")

    def _setup_ui(self):
        """Szél konstans heatmap tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Heatmap beágyazása
        layout.addWidget(self.wind_heatmap)

    def update_data(self, data: Dict[str, Any]):
        """🎯 Szél konstans heatmap frissítés - BEAUFORT PROGRESSZÍV SZÍNSKÁLA (ÁLGADOS MAX)"""
        try:
            # 🔍 DEBUG - Szél adatok ellenőrzése
            daily_data = data.get('daily', {})
            logger.debug(f"DEBUG SZÉL TAB - Elérhető daily adatok: {list(daily_data.keys())}")

            wind_param = 'windspeed_10m_max'  # ✅ VALÓS API NÉV

            if not daily_data.get(wind_param):
                logger.warning("Nincs elérhető windspeed_10m_max adat")
                return

            # 🎨 BEAUFORT-ALAPÚ 13 FOKOZAT SZÍNSKÁLA BEÁLLÍTÁSA
            self.wind_heatmap._custom_cmap = self.wind_cmap
            self.wind_heatmap._custom_norm = self.wind_norm
            self.wind_heatmap.parameter = wind_param
            logger.debug(f"🎨 Szél BEAUFORT colormap beállítva: {type(self.wind_cmap)}, param: {wind_param}")

            # ✅ DIREKT ADATÁTADÁS - aggregáció a heatmap chart-ban történik
            self.wind_heatmap.update_data(data)

            logger.info("💨 Szél KONSTANS HEATMAP tab frissítve (BEAUFORT 13 fokozat, átlagos max)")

        except Exception as e:
            logger.error(f"WindTabWidget KONSTANS HEATMAP frissítési hiba: {e}")


class WindGustTabWidget(QWidget):
    """🌪️ Max Széllökés tab - KONSTANS HEATMAP (BEAUFORT-alapú 13 fokozat progresszív színskála) - SZÉLLÖKÉSEK"""

    def __init__(self):
        super().__init__()

        # HEATMAP CHART - SZÉLLÖKÉS VERZIÓ (MAX GUSTS)
        self.windgust_heatmap = HeatmapCalendarChart()
        self.windgust_heatmap.figure.set_size_inches(20, 10)  # EXTRA NAGY MÉRET
        self.windgust_heatmap.parameter = "wind_gusts_max"  # ✅ VALÓS API NÉV
        self.windgust_heatmap.chart_title = "🌪️ Konstans Max Széllökés Heatmap (wind_gusts_max)"

        # 🎨 BEAUFORT-ALAPÚ 13 FOKOZAT SZÉL SZÍNSKÁLA (UGYANAZ, MINT A SZÉL TAB)
        self.windgust_cmap, self.windgust_norm = MeteorologicalColorMaps.get_wind_colormap()

        self._setup_ui()
        logger.info("WindGustTabWidget inicializálva - KONSTANS HEATMAP (365 téglalap, BEAUFORT 13 fokozat, max széllökések)")

    def _setup_ui(self):
        """Max széllökés konstans heatmap tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Heatmap beágyazása
        layout.addWidget(self.windgust_heatmap)

    def update_data(self, data: Dict[str, Any]):
        """🎯 Max széllökés konstans heatmap frissítés - BEAUFORT PROGRESSZÍV SZÍNSKÁLA (SZÉLLÖKÉSEK)"""
        try:
            # 🔍 DEBUG - Széllökés adatok ellenőrzése
            daily_data = data.get('daily', {})
            logger.debug(f"DEBUG MAX SZÉLLÖKÉS TAB - Elérhető daily adatok: {list(daily_data.keys())}")

            windgust_param = 'wind_gusts_max'  # ✅ VALÓS API NÉV (nincs 10m!)

            if not daily_data.get(windgust_param):
                logger.warning("Nincs elérhető wind_gusts_max adat")
                return

            # 🎨 BEAUFORT-ALAPÚ 13 FOKOZAT SZÍNSKÁLA BEÁLLÍTÁSA
            self.windgust_heatmap._custom_cmap = self.windgust_cmap
            self.windgust_heatmap._custom_norm = self.windgust_norm
            self.windgust_heatmap.parameter = windgust_param
            logger.debug(f"🎨 Széllökés BEAUFORT colormap beállítva: {type(self.windgust_cmap)}, param: {windgust_param}")

            # ✅ DIREKT ADATÁTADÁS - aggregáció a heatmap chart-ban történik
            self.windgust_heatmap.update_data(data)

            logger.info("🌪️ Max Széllökés KONSTANS HEATMAP tab frissítve (BEAUFORT 13 fokozat)")

        except Exception as e:
            logger.error(f"WindGustTabWidget KONSTANS HEATMAP frissítési hiba: {e}")


class ClimateTabWidget(QTabWidget):
    """🌡️ Klímakutató tab widget - 4 KONSTANS HEATMAP TAB + 2 DEDICATED WIND CHART - BEAUFORT + MAX SZÉLLÖKÉS VERZIÓ"""

    def __init__(self):
        super().__init__()

        # Tab widget-ek létrehozása - KONSTANS HEATMAP VERZIÓK
        self.temp_tab = TemperatureTabWidget()      # 🌡️ Hőmérséklet KONSTANS HEATMAP
        self.precip_tab = PrecipitationTabWidget()  # 🌧️ Csapadék KONSTANS HEATMAP
        self.wind_tab = WindTabWidget()             # 💨 Szél KONSTANS HEATMAP (BEAUFORT, átlagos max)
        self.windgust_tab = WindGustTabWidget()     # 🌪️ Max Széllökés KONSTANS HEATMAP (BEAUFORT, gusts)

        # 🌪️ DEDICATED WIND CHARTOK HOZZÁADÁSA
        self.dedicated_wind_chart = WindChart()     # 🌪️ WindChart dedicated
        self.dedicated_windrose_chart = WindRoseChart()  # 🌹 WindRoseChart dedicated

        self._setup_tabs()

        # Lazy loading tracking
        self.data_cache = None
        self.tabs_initialized = {'temp': False, 'precip': False, 'wind': False, 'windgust': False, 'wind_chart': False, 'windrose_chart': False}

        # Tab változás figyelése
        self.currentChanged.connect(self._on_tab_changed)

        logger.info("ClimateTabWidget inicializálva - 4 KONSTANS HEATMAP TAB + 2 DEDICATED WIND CHART (365 téglalap, BEAUFORT szél + max széllökés)")

    def _setup_tabs(self):
        """Tab-ok beállítása - KONSTANS HEATMAP-EK + MAX SZÉLLÖKÉS + DEDICATED WIND CHARTOK"""
        # Tab-ok hozzáadása
        self.addTab(self.temp_tab, "🌡️ Hőmérséklet")         # KONSTANS HEATMAP
        self.addTab(self.precip_tab, "🌧️ Csapadék")           # KONSTANS HEATMAP (0mm=fehér)
        self.addTab(self.wind_tab, "💨 Szél")                 # KONSTANS HEATMAP (BEAUFORT, átlagos max)
        self.addTab(self.windgust_tab, "🌪️ Max Széllökés")   # KONSTANS HEATMAP (BEAUFORT, max gusts)

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
            daily_data = data.get('daily', {})
            dates = daily_data.get('time', [])
            total_days = len(dates)

            logger.info(f"🎯 ClimateTabWidget frissítve - {total_days} nap → 365 téglalap/tab (BEAUFORT szél + max széllökés)")

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
                self.tabs_initialized['temp'] = True
            elif index == 1:  # Csapadék tab (konstans heatmap, 0mm=fehér)
                self.precip_tab.update_data(self.data_cache)
                self.tabs_initialized['precip'] = True
            elif index == 2:  # Szél tab (konstans heatmap, BEAUFORT, átlagos max)
                self.wind_tab.update_data(self.data_cache)
                self.tabs_initialized['wind'] = True
            elif index == 3:  # Max Széllökés tab (konstans heatmap, BEAUFORT, max gusts)
                self.windgust_tab.update_data(self.data_cache)
                self.tabs_initialized['windgust'] = True
            elif index == 4:  # 🌪️ DEDICATED WindChart tab
                self.dedicated_wind_chart.update_data(self.data_cache)
                self.tabs_initialized['wind_chart'] = True
                logger.debug("DEDICATED WindChart tab aktívált és frissítve!")
            elif index == 5:  # 🌹 DEDICATED WindRoseChart tab
                self.dedicated_windrose_chart.update_data(self.data_cache)
                self.tabs_initialized['windrose_chart'] = True
                logger.debug("DEDICATED WindRoseChart tab aktívált és frissítve!")

        except Exception as e:
            logger.error(f"Tab {index} frissítési hiba: {e}")


__all__ = [
    "TemperatureTabWidget",
    "PrecipitationTabWidget",
    "WindTabWidget",
    "WindGustTabWidget",
    "ClimateTabWidget",
]
