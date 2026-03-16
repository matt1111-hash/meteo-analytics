#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Temperature Chart - Core

🌡️ Enhanced Temperature Chart - Main class

Képességek:
- Main EnhancedTemperatureChart class
- Data update handling
- Theme integration
- Initialization

Fájl: src/presentation/gui/charts/temperature_chart/core.py
"""

from typing import Any, Dict, Optional

from PySide6.QtWidgets import QWidget

from ..base_chart import WeatherChart
from ..tooltip_mixin import WeatherTooltipMixin
from .data_extractor import TemperatureDataExtractor
from .formatting import TemperatureFormattingMixin
from .plotting import TemperaturePlottingMixin
from .tooltip_handler import TemperatureTooltipHandlerMixin


class EnhancedTemperatureChart(
    TemperatureTooltipHandlerMixin,
    TemperatureFormattingMixin,
    TemperaturePlottingMixin,
    WeatherChart,
    WeatherTooltipMixin,
):
    """
    Fejlett hőmérséklet grafikon widget - PROFESSZIONÁLIS NAGY VERZIÓ + DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER.
    Színes zónák, trend vonalak, statisztikai elemek.
    🎨 TÉMA INTEGRÁCIÓ: ColorPalette használata professzionális színválasztáshoz
    🔧 KRITIKUS JAVÍTÁS: Robusztus update cycle duplikáció nélkül + LEGEND POZÍCIÓ JAVÍTVA
    🎯 TOOLTIP ENHANCEMENT: WeatherTooltipMixin integráció - INTERAKTÍV HOVER/CLICK FUNKCIÓK
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(figsize=(14, 8), parent=parent)  # NAGY MÉRET
        self.chart_title = "🌡️ Részletes Hőmérséklet Elemzés"
        self.y_label = "Hőmérséklet (°C)"

        # 🎯 TOOLTIP AKTIVÁLÁS - OPT-IN RENDSZER
        self.enable_tooltips(hover_tolerance=15)
        print("🎯 DEBUG: EnhancedTemperatureChart tooltip-ok aktiválva!")

    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes hőmérséklet chart frissítés + SIMPLIFIED THEMEMANAGER SZÍNEK.
        """
        print(
            "🌡️ DEBUG: EnhancedTemperatureChart.update_data() - DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER VERZIÓ"
        )

        try:
            # Duplikáció ellenőrzés
            if self._is_updating:
                print("⚠️ DEBUG: Update már folyamatban, skip")
                return

            self._is_updating = True

            df = TemperatureDataExtractor.extract_temperature_data(data)
            if df.empty:
                print("⚠️ DEBUG: Üres DataFrame, chart törlése")
                self.clear_chart()
                return

            self.current_data = df
            self._last_update_data = data.copy()

            # === KRITIKUS: TELJES FIGURE TÖRLÉSE DUPLIKÁCIÓ ELLEN ===
            print("🧹 DEBUG: Figure.clear() hívása duplikáció ellen")
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)

            # 🎨 TÉMA ALKALMAZÁSA
            self._apply_theme_to_chart()

            # Chart megrajzolása
            self._plot_enhanced_temperature(df)

            # Finalizálás
            self.draw()
            self._is_updating = False

            print(
                "✅ DEBUG: EnhancedTemperatureChart frissítés kész - DUPLIKÁCIÓ MENTES + THEMED + TOOLTIP READY"
            )

        except Exception as e:
            print(f"❌ DEBUG: Enhanced hőmérséklet chart hiba: {e}")
            self._is_updating = False
            self.clear_chart()
