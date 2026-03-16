# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from analytics_tabs.py."""

from __future__ import annotations

from .analytics_tabs_support import *


class WindGustTabWidget(QWidget):
    """🌪️ Max Széllökés tab - KONSTANS HEATMAP (BEAUFORT-alapú 13 fokozat progresszív színskála) - SZÉLLÖKÉSEK"""

    def __init__(self):
        super().__init__()

        # HEATMAP CHART - SZÉLLÖKÉS VERZIÓ (MAX GUSTS)
        self.windgust_heatmap = HeatmapCalendarChart()
        self.windgust_heatmap.figure.set_size_inches(20, 10)  # EXTRA NAGY MÉRET
        self.windgust_heatmap.parameter = "wind_gusts_max"  # ✅ VALÓS API NÉV
        self.windgust_heatmap.chart_title = (
            "🌪️ Konstans Max Széllökés Heatmap (wind_gusts_max)"
        )

        # 🎨 BEAUFORT-ALAPÚ 13 FOKOZAT SZÉL SZÍNSKÁLA (UGYANAZ, MINT A SZÉL TAB)
        self.windgust_cmap, self.windgust_norm = (
            MeteorologicalColorMaps.get_wind_colormap()
        )

        self._setup_ui()
        logger.info(
            "WindGustTabWidget inicializálva - KONSTANS HEATMAP (365 téglalap, BEAUFORT 13 fokozat, max széllökések)"
        )

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
            daily_data = data.get("daily", {})
            logger.debug(
                f"DEBUG MAX SZÉLLÖKÉS TAB - Elérhető daily adatok: {list(daily_data.keys())}"
            )

            windgust_param = "wind_gusts_max"  # ✅ VALÓS API NÉV (nincs 10m!)

            if not daily_data.get(windgust_param):
                logger.warning("Nincs elérhető wind_gusts_max adat")
                return

            # 🎨 BEAUFORT-ALAPÚ 13 FOKOZAT SZÍNSKÁLA BEÁLLÍTÁSA
            self.windgust_heatmap._custom_cmap = self.windgust_cmap
            self.windgust_heatmap._custom_norm = self.windgust_norm
            self.windgust_heatmap.parameter = windgust_param
            logger.debug(
                f"🎨 Széllökés BEAUFORT colormap beállítva: {type(self.windgust_cmap)}, param: {windgust_param}"
            )

            # ✅ DIREKT ADATÁTADÁS - aggregáció a heatmap chart-ban történik
            self.windgust_heatmap.update_data(data)

            logger.info(
                "🌪️ Max Széllökés KONSTANS HEATMAP tab frissítve (BEAUFORT 13 fokozat)"
            )

        except Exception as e:
            logger.error(f"WindGustTabWidget KONSTANS HEATMAP frissítési hiba: {e}")
